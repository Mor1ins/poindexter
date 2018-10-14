#! /usr/bin/env python
# -*- coding: utf-8 -*-

from os import listdir
from PIL import Image
from os.path import isfile, join
from zipfile import ZipFile
from urllib import request
from Loaders.VkLoader import VkUploader
from fpdf import FPDF
from dependency import handlers, view_api, work_dir


@handlers.message_handler([u"Погнали", u"погнали", u"лол", u"Лол"])
def start_handler(message):
    view_api.vk.messages.send(user_id=message.user_id, message=u"Повеливайте, господин!")


@handlers.message_handler([u"Загрузить с вк"])
def vk_start_download_handler(message):
    view_api.vk.messages.send(user_id=message.user_id, message=u"Жду архив (отправьте его, а потом отправьте ОК)")


@handlers.message_handler([u"Ок", u'ОК', u"ок"])
def vk_ready_download_handler(message):
    view_api.vk.messages.send(user_id=message.user_id, message=u"Погнали!")

    response = view_api.vk.messages.getHistoryAttachments(peer_id=message.user_id, media_type=u"doc", count=1)

    title = response['items'][0]['attachment']['doc']['title'].split('.')[0]
    source = response['items'][0]['attachment']['doc']['url']
    ext = response['items'][0]['attachment']['doc']['ext']

    if ext != "zip":
        view_api.vk.messages.send(user_id=message.user_id, message=u"Неправильный формат файла")
        return

    dest_for_archive = work_dir % ("%s.%s" % (title, ext))
    request.urlretrieve(source, dest_for_archive)

    view_api.vk.messages.send(user_id=message.user_id, message=u"Файл скачали")

    archive_file = ZipFile(dest_for_archive)
    archive_file.extractall(work_dir % title)
    archive_file.close()

    photos = [work_dir % (title + "/" + f)
              for f in listdir(work_dir % title)
              if isfile(join(work_dir % title, f))]

    view_api.vk.messages.send(user_id=message.user_id, message=u"Разархивировали")

    pdf = FPDF()
    for image in photos:
        pdf.add_page()
        file = Image.open(image)
        box = file.getbbox()
        pdf.image(image, x=box[0], y=box[1], w=pdf.w, h=pdf.h)
    pdf.output(work_dir % ("%s.%s" % (title, "pdf")), "F")

    view_api.vk.messages.send(user_id=message.user_id, message=u"Пдф сгенерирована")

    doc = VkUploader().messages_save(work_dir % ("%s.%s" % (title, "pdf")), 'doc', message.user_id, title)

    view_api.vk.messages.send(user_id=message.user_id, message=u"Загружаем на сервер")

    view_api.vk.messages.send(peer_id=message.user_id, attachment='doc%s_%s' % (doc['owner_id'], doc['id']))


def get_handlers():
    return handlers
