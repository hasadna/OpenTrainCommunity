from lxml import html
import requests

def get_depture_time(orgid, destid, day, month, year, hour):

    """ Extract depture times from the official Israel Railways' site
    Args:
        orgid: Station's id which the train depture from
        destid: Station's id which the train goes
        day: the day of the month when the ride takes place(integer from 1 to 31 according to the month)
        month: the month when the ride takes place (integer from 1 to 12)
        year: the year when the ride takes place(integer in the scheme of YYYY)
        hour: the hour when the ride takes place (integer from 0 to 23)

    Returns:
        A list of the departure hours according to the arguments

        example:
        ['0:52', '1:52', '2:52', '3:52', '4:35']

        If the list is returned empty there's no depture times whith the chosen arguments

    """
    allhours = []
    #the list that will contain all the depture hours and will get returned
    urlstr = ('https://www.rail.co.il/HE/DrivePlan/Pages/DrivePlan.aspx?DrivePlanPage=true&'
                         'OriginStationId={}&'
                         'DestStationId={}&'
                         'HoursDeparture={}&'
                         'MinutesDeparture=0&'
                         'GoingTrainCln={}-{}-{}&'
                         'IsFullURL=true').format(orgid,destid,hour,year,month,day)

    page = requests.get(urlstr)
    html_tree = html.fromstring(page.content)
    i = 0
    # loops thats exports the depture times until theres no depture times in the html file
    while (len(hours) != 0 or i == 0):
        hours = html_tree.xpath('//tr[@id="{}"]/td[position()=2]/text()'.format(i))
        allhours.append(hours[0])
        i = i + 1

    return allhours
