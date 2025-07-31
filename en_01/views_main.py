# ! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
import datetime

from django.http import JsonResponse, HttpResponse
from django.contrib import auth
from django.shortcuts import render, redirect
from .service.service import get_main_args
from .motor_control import turn_on_motor, turn_off_motor, set_last_button_pressed


def error403(request, reason=""):
    return redirect('/')


def index(request):
    args = get_main_args(request, section="main")
    args['main_tab'] = 'cabinet/cabinet_01.html'
    return render(request, args['main_tab'], args)


def motor_act(request):
    print("motor_act")
    answer = {"AnswerCod": "01",
              "AnswerText": "ERROR"}
    if request.method == "POST":
        print("POST = ", request.POST)
        m_act = request.POST.get('f_act', "").strip()
        if m_act == "off":
            print("motor_off")
            set_last_button_pressed("OFF")
            m_return = turn_off_motor()
            answer = {"AnswerCod": "00",
                      "AnswerText": m_return}
        elif m_act == "on":
            print("motor_on")
            set_last_button_pressed("ON")
            m_return = turn_on_motor()
            answer = {"AnswerCod": "00",
                      "AnswerText": m_return}
        else:
            answer = {"AnswerCod": "01",
                      "AnswerText": "Invalid action. Use 'on' or 'off'."}
    else:
            answer = {"AnswerCod": "01",
                      "AnswerText": "Invalid request method. POST required."}
    return JsonResponse(answer)
