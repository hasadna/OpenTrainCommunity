// app.js
"use strict";

$("#logout_link").click(function() {
    $("#username").text('??');
    $.post('/browse/api/logout/').done(function(d) {
        refresh_login(d);
    }).fail(function(d) {
        check_login();
    });
});

$("#login_form").submit(function() {
    $('#login_error').addClass('hideit');
    $.post('/browse/api/login/',{
        name: $("#name").val(),
        password: $("#password").val(),
    }).done(function(d) {
        refresh_login(d);
        $('#myModal').modal('hide');
    }).fail(function(d) {
        $('#login_error').removeClass('hideit');
    });
    return false;
});


function refresh_login(data) {
    if (data.logged_in) {
        $("#login_li").addClass("hideit");
        $("#username").text(data.username);
        $("#logout_li").removeClass("hideit");
    } else {
        $("#login_li").removeClass("hideit");
        $("#logout_li").addClass("hideit");
    }
}

function check_login() {
    $.get('/browse/api/logged-in/').success(function(data) {
        refresh_login(data);
    });
}

$(check_login);
