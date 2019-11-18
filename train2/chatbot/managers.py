import functools
import json
import logging


from django.conf import settings
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from . import models
from chatbot.templatetags.chatbot_tags import strip_seconds

logger = logging.getLogger(__name__)


def il_time(dt):
    return dt.astimezone(timezone.get_default_timezone())


def _get_chat_id(update):
    return update.message.chat_id if update.message else update.callback_query.message.chat_id


def _report_to_button(report):
    title = _report_title(report)
    return InlineKeyboardButton(text=title, callback_data=f'admin_report:show:{report.id}')


def _report_title(report):
    ctime = il_time(report.created_at).strftime('%H:%M')
    wrong = '' if not report.wrong_report else '[' + 'מסומן כשגוי' + ']'
    return f'''(#{report.id} {ctime}) {strip_seconds(report.first_stop['departure_time'])} {report.first_stop['stop_name']} - {report.last_stop['stop_name']} {wrong}'''


def verify_manager(func):
    @functools.wraps(func)
    def wrapper(bot, update):
        chat_id = _get_chat_id(update)
        admin_name = settings.ADMIN_CHAT_IDS.get(str(chat_id), None)
        if admin_name is None:
            bot.send_message(chat_id, 'סליחה - רק מנהלים בבקשה')
            return
        else:
            func(bot, update)
    return wrapper


@verify_manager
def handle_cmd(bot, update):
    chat_id = update.message.chat_id
    show_list(bot, chat_id)


def show_list(bot, chat_id, before_pk=None):
    qs = models.ChatReport.objects.order_by('-created_at')
    if before_pk:
        qs = qs.filter(pk__lt=before_pk)
    last_reports = list(qs[0:10])
    if last_reports:
        show_more = [
            [get_show_more_button(last_reports[-1].pk)]
        ]
    else:
        show_more = []
    buttons = InlineKeyboardMarkup(
        [
            [_report_to_button(r)] for r in last_reports
        ] + show_more
    )
    admin_name = settings.ADMIN_CHAT_IDS[str(chat_id)]
    return bot.send_message(
        chat_id,
        'שלום ' + admin_name + ' אנא בחר את אחד מהדיווחים הבאים להמשך ',
        reply_markup=buttons
    )


@verify_manager
def handle_callback(bot, update):
    logger.info(json.dumps(update.to_dict(), indent=4))
    chat_id = _get_chat_id(update)
    data = update.callback_query.data
    admin_prefix, cmd, report_id = data.split(':')
    report_id = int(report_id)
    logger.info('cmd = %s report_id = %d', cmd, report_id)
    with transaction.atomic():
        if cmd == 'list':
            return show_list(bot, chat_id, before_pk=report_id)

        bot.delete_message(chat_id, update.callback_query.message.message_id)
        report = models.ChatReport.objects.get(pk=report_id)
        if cmd == 'show':
            return show_report(bot, chat_id, report)
        if cmd == 'del_notify':
            return del_report(bot, chat_id, report, notify=True)
        if cmd == 'del_silent':
            return del_report(bot, chat_id, report, notify=False)
        if cmd == 'undel_silent':
            return undel_report(bot, chat_id, report, notify=False)


def get_line(t, a, rid):
    return (
        [
            InlineKeyboardButton(
                text=t,
                callback_data=f'admin_report:{a}:{rid}')
        ]
    )


def get_show_more_button(before_pk=None):
    return InlineKeyboardButton(text='*** הצג עוד ***', callback_data=f'admin_report:list:{before_pk}')


def get_list_markup():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(text='הצג רשימה', callback_data=f'admin_report:list:0')
    ]])


def show_report(bot, chat_id, report):
    ctime = il_time(report.created_at).strftime('%H:%M')

    report_text = render_to_string('chatbot/new_report_message.html', context={
        'report': report,
    }).strip()
    report_text += '\n' + 'הדיווח התקבל בשעה ' + ctime
    if report.wrong_report:
        report_text += '\nהדיווח כרגע מסומן כדיווח שגוי'
    report_text += '\n\nאנא בחרו אחת מהפעולות הבאות' + ":"

    if not report.wrong_report:
        buttons = [
            get_line('סמן כשגוי ושלח הודעה בערוץ', 'del_notify', report.id),
            get_line('סמן כשגוי ללא שליחת הודעה', 'del_silent', report.id),
        ]
    else:
        buttons = [
            get_line('בטל סימון כשגוי', 'undel_silent', report.id),
        ]

    bot.send_message(
        chat_id,
        text=report_text,
        parse_mode='html',
        disable_web_page_preview=True,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


def _to_msg(report, text):
    return _report_title(report) + '\n' + text


def del_report(bot, chat_id, report, *, notify):
    from . import broadcast
    report.mark_as_wrong(notify=notify)
    notif_msg = 'ונשלחה הודעה בערוץ' if notify else ''
    bot.send_message(
        chat_id,
        text=_to_msg(report, 'הנסיעה סומנה כשגויה' + ' ' + notif_msg),
        parse_mode='html',
        disable_web_page_preview=True,
        reply_markup=get_list_markup()
    )
    if notify:
        broadcast.broadcast_wrong_report_to_telegram_channel(report)


def undel_report(bot, chat_id, report, *, notify):
    assert not notify, "notify is not supported for now"
    if not report.wrong_report:
        bot.send_message(
            chat_id,
            text=_to_msg(report, 'הנסיעה איננה מסומנת כשגויה'),
            parse_mode='html',
            disable_web_page_preview=True,
            reply_markup=get_list_markup()
        )
        return
    report.wrong_report = False
    report.save()
    bot.send_message(
        chat_id,
        text=_to_msg(report,'סימון הנסיעה כשגיאה בוטל'),
        parse_mode='html',
        disable_web_page_preview=True,
        reply_markup=get_list_markup()
    )
