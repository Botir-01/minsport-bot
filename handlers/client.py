from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from keyboards.inline_keyboards import languages_keyboard, agree_keyboard, choose_keyboard, check_person, \
    cancel_keyboard, confirm_keyboard
from create_bot import dp, bot
from aiogram.types import ParseMode
from decouple import config

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib


async def welcome(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    await state.update_data(user_id=user_id, username=message.from_user.username)
    await state.set_state("get_lang")
    markup = await languages_keyboard()
    await message.reply("Tilni tanlang / Выберите язык", reply_markup=markup, parse_mode=ParseMode.HTML)


async def privacy_agree(message: types.Message, state: FSMContext):
    call_data = message.text
    user_id = message.from_user.id
    if call_data == '🇷🇺Русский язык':
        markup = await agree_keyboard("ru")
        await state.update_data(lang="ru")
        text = "Здравствуйте, добро пожаловать в бот, созданного для борьбы с коррупцией и антикоррупционной " \
               "деятельностью в сфере развития спорта!\n\n<b>Важный!</b> Закон Республики Узбекистан «<b>О персональных данных</b>» " \
               "предусматривает трансграничную передачу данных физических лиц только при наличии согласия физических " \
               "лиц на трансграничную передачу персональных данных.\n\nДля того, чтобы использовать " \
               "@motach_anticorruption_bot в соответствии с данным законом, " \
               "вы должны дать согласие на использование вашей личной информации. "
    else:
        markup = await agree_keyboard("uz")
        await state.update_data(lang="uz")
        text = "Assalomu alaykum, Sportni rivojlantirish sohasida korrupsion holatlarni va korrupsiyaga doir faoliyatlarga " \
               "qarshi kurashish uchun yaratilgan botga xush kelibsiz! \n\n<b>Muxim!</b> Jismoniy shaxslarning o‘z shaxsiga " \
               "ta’luqli ma’lumotlarini transchegaraviy uzatishga roziligi mavjud bo‘lgan taqdirdagina ma’lumotlarni " \
               "transchegaraviy uzatishning amalga oshirilishi O‘zbekiston Respublikasining  “Shaxsga doir " \
               "ma’lumotlar to‘g‘risida”gi Qonunda nazarda tutilgan. \n\nMazkur qonunga asosan " \
               "@motach_anticorruption_bot dan foydalanish uchun Sizning " \
               "shaxsingizga doir ma’lumotlaringizdan foydalanishga rozilik bildirishingiz lozim. "
    await bot.send_message(chat_id=user_id, text=text, parse_mode=ParseMode.HTML, reply_markup=markup)
    await state.set_state("choose")


async def choose(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text = message.text
    lang = data.get("lang")
    if lang == "uz":
        if text == "✅Roziman":
            data = "confirm"
        else:
            data = "cancel"
        text = "Ma’qul variantni tanlang:"
    else:
        if text == "✅Я согласен":
            data = "confirm"
        else:
            data = "cancel"
        text = "Выберите нужный вариант:"

    if data == "confirm":
        markup = await choose_keyboard(lang)
        await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=markup)
        await state.set_state("legal")
    else:
        markup = await languages_keyboard()
        await bot.send_message(chat_id=message.from_user.id, text="Tilni tanlang / Выберите язык", reply_markup=markup,
                               parse_mode=ParseMode.HTML)
        await state.set_state("get_lang")


async def choose_person_type(message: types.Message, state: FSMContext):
    data = await state.get_data()
    text_message = message.text
    lang = data.get("lang")
    if lang == "uz":
        text = "Shaxs turini tanlang:"
    else:
        text = "Выберите тип лица:"
    markup = await check_person(lang)
    await state.update_data(choose=text_message)
    await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=markup)
    await state.set_state("appeal_type")


async def get_appeal_type(message: types.Message, state: FSMContext):
    message_text = message.text
    data = await state.get_data()
    lang = data.get("lang")
    user_choice = ''
    choosing = data.get("choose")
    if lang == "uz":
        if choosing == "🖊 Taklif va tavsiyalar yuborish":
            user_choice = "taklif"
        elif choosing == "📩 Murojaat va shikoyatlar yuborish":
            user_choice = "murojaat"
        else:
            user_choice = "boshqa"
    if user_choice == "taklif":
        if lang == "uz":
            text = "Taklif va tavsiyalar beruvchi F.I.Shni kiriting"
        else:
            text = "Введите Ф.И.О лица, делающего предложение и рекомендации"
        await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=types.ReplyKeyboardRemove())
        await state.set_state("phone_number")
    elif user_choice == "murojaat":
        if lang == "uz":
            text = "Murojaat va shikoyatlar beruvchi F.I.Shni kiriting"
        else:
            text = "Введите Ф.И.О лица, подающего жалобу и претензии"
        await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=types.ReplyKeyboardRemove())
        await state.set_state("location")
    else:
        if lang == "uz":
            text = "F.I.Shni kiriting"
        else:
            text = "Введите Ф.И.О"
        await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=types.ReplyKeyboardRemove())
        await state.set_state("location")


async def get_phone_number(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")
    name = message.text
    await state.update_data(name=name)
    if lang == "uz":
        text = "📞 Telefon raqamingiz "
    else:
        text = "📞 Ваш номер телефона"
    await bot.send_message(chat_id=message.from_user.id, text=text)
    await state.set_state("text")


async def get_location(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")
    name = message.text
    await state.update_data(name=name)
    if lang == "uz":
        text = "📍 Manzilingizni kiriting"
    else:
        text = "📍 Введите свой адрес"
    await bot.send_message(chat_id=message.from_user.id, text=text)
    await state.set_state("phone_number_two")


async def get_phone_number_two(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")
    address = message.text
    await state.update_data(address=address)
    if lang == "uz":
        text = "Telefon raqamingiz "
    else:
        text = "📞 Ваш номер телефона"
    await bot.send_message(chat_id=message.from_user.id, text=text)
    await state.set_state("text")


async def get_text_from_user(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")
    if lang == "uz":
        text = "📄 Murojaat matnini kiriting"
    else:
        text = "📄 Введите текст сообщения"
    phone = message.text
    await state.update_data(phone=phone)
    await bot.send_message(chat_id=message.from_user.id, text=text)
    await state.set_state("main_file_text")


async def main_file_text(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang")
    if lang == "uz":
        text = "Tegishli fayllarni biriktiring (video, audio, tekst va boshqalar)"
    else:
        text = "Прикрепите соответствующие файлы (видео, аудио, текст и т. д.)"
    main = message.text
    await state.update_data(main_text=main)
    markup = await cancel_keyboard(lang)
    await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=markup)
    await state.set_state("main_file")


async def main_document(message: types.Message, state: FSMContext):
    file_id = message.document.file_id
    data = await state.get_data()
    name = message.document.file_name
    await message.document.download(destination=f"files/{name}")
    lang = data.get("lang")
    if lang == 'uz':
        text = f"<b>Kimdan: </b> {data.get('name')}\n" \
               f"<b>Telefon raqami: </b> {data.get('phone')}\n" \
               f"<b>Foydalanuvchi nomi: </b> @{data.get('username')}\n" \
               f"<b>Murojaat turi: </b> {data.get('choose')}\n" \
               f"<b>Murojaat matni: </b> {data.get('main_text')}\n"
    else:
        text = f"<b>От кого: </b> {data.get('name')}\n" \
               f"<b>Номер телефона: </b> {data.get('phone')}\n" \
               f"<b>Имя пользователя: </b> @{data.get('username')}\n" \
               f"<b>Тип: </b> {data.get('choose')}\n" \
               f"<b>Текст: </b> {data.get('main_text')}\n"
    await state.update_data(body=text, file_name=name, file_type="only")
    markup = await confirm_keyboard(data.get('lang'))
    await bot.send_document(chat_id=message.from_user.id, document=file_id, caption=text, reply_markup=markup,
                            parse_mode=ParseMode.HTML)
    await state.set_state("for_end")


async def main_photo(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    data = await state.get_data()
    file_name = f"{file_id}.jpg"
    await message.photo[-1].download(destination=f"files/{file_id}.jpg")
    lang = data.get("lang")
    if lang == 'uz':
        text = f"<b>Kimdan: </b> {data.get('name')}\n" \
               f"<b>Telefon raqami: </b> {data.get('phone')}\n" \
               f"<b>Foydalanuvchi nomi: </b> @{data.get('username')}\n" \
               f"<b>Murojaat turi: </b> {data.get('choose')}\n" \
               f"<b>Murojaat matni: </b> {data.get('main_text')}\n"
    else:
        text = f"<b>От кого: </b> {data.get('name')}\n" \
               f"<b>Номер телефона: </b> {data.get('phone')}\n" \
               f"<b>Имя пользователя: </b> @{data.get('username')}\n" \
               f"<b>Тип: </b> {data.get('choose')}\n" \
               f"<b>Текст: </b> {data.get('main_text')}\n"
    await state.update_data(body=text, file_name=file_name, file_type="only")
    markup = await confirm_keyboard(data.get('lang'))
    await bot.send_photo(chat_id=message.from_user.id, photo=file_id, caption=text, reply_markup=markup,
                         parse_mode=ParseMode.HTML)
    await state.set_state("for_end")


async def main_video(message: types.Message, state: FSMContext):
    file_id = message.video.file_id
    data = await state.get_data()
    await message.video.download(destination=f"files/{message.video.file_name}")
    lang = data.get("lang")
    if lang == 'uz':
        text = f"<b>Kimdan: </b> {data.get('name')}\n" \
               f"<b>Telefon raqami: </b> {data.get('phone')}\n" \
               f"<b>Foydalanuvchi nomi: </b> @{data.get('username')}\n" \
               f"<b>Murojaat turi: </b> {data.get('choose')}\n" \
               f"<b>Murojaat matni: </b> {data.get('main_text')}\n"
    else:
        text = f"<b>От кого: </b> {data.get('name')}\n" \
               f"<b>Номер телефона: </b> {data.get('phone')}\n" \
               f"<b>Имя пользователя: </b> @{data.get('username')}\n" \
               f"<b>Тип: </b> {data.get('choose')}\n" \
               f"<b>Текст: </b> {data.get('main_text')}\n"
    await state.update_data(body=text, file_name=message.video.file_name, file_type="only")
    dat = await state.get_data()
    markup = await confirm_keyboard(data.get('lang'))
    await bot.send_video(chat_id=message.from_user.id, video=file_id, caption=text, reply_markup=markup,
                         parse_mode=ParseMode.HTML)
    await state.set_state("for_end")


async def main_audio_voice(message: types.Message, state: FSMContext):
    file_id = message.voice.file_id
    file_name = f"{file_id}.ogg"
    data = await state.get_data()
    await message.voice.download(destination=f"files/{file_id}.ogg")
    lang = data.get("lang")
    if lang == 'uz':
        text = f"<b>Kimdan: </b> {data.get('name')}\n" \
               f"<b>Telefon raqami: </b> {data.get('phone')}\n" \
               f"<b>Foydalanuvchi nomi: </b> @{data.get('username')}\n" \
               f"<b>Murojaat turi: </b> {data.get('choose')}\n" \
               f"<b>Murojaat matni: </b> {data.get('main_text')}\n"
    else:
        text = f"<b>От кого: </b> {data.get('name')}\n" \
               f"<b>Номер телефона: </b> {data.get('phone')}\n" \
               f"<b>Имя пользователя: </b> @{data.get('username')}\n" \
               f"<b>Тип: </b> {data.get('choose')}\n" \
               f"<b>Текст: </b> {data.get('main_text')}\n"
    await state.update_data(body=text, file_name=message.video.file_name, file_type="only")
    markup = await confirm_keyboard(data.get('lang'))
    await bot.send_voice(chat_id=message.from_user.id, voice=file_id, caption=text, reply_markup=markup,
                         parse_mode=ParseMode.HTML)
    await state.set_state("for_end")


async def main_audio_file(message: types.Message, state: FSMContext):
    data = await state.get_data()
    audio = message.audio
    await message.audio.download(destination=f"files/{audio.file_name}")
    lang = data.get("lang")
    if lang == 'uz':
        text = f"<b>Kimdan: </b> {data.get('name')}\n" \
               f"<b>Telefon raqami: </b> {data.get('phone')}\n" \
               f"<b>Foydalanuvchi nomi: </b> @{data.get('username')}\n" \
               f"<b>Murojaat turi: </b> {data.get('choose')}\n" \
               f"<b>Murojaat matni: </b> {data.get('main_text')}\n"
    else:
        text = f"<b>От кого: </b> {data.get('name')}\n" \
               f"<b>Номер телефона: </b> {data.get('phone')}\n" \
               f"<b>Имя пользователя: </b> @{data.get('username')}\n" \
               f"<b>Тип: </b> {data.get('choose')}\n" \
               f"<b>Текст: </b> {data.get('main_text')}\n"
    await state.update_data(body=text, file_name=message.audio.file_name, file_type="only")
    markup = await confirm_keyboard(data.get('lang'))
    await bot.send_audio(chat_id=message.from_user.id, audio=audio.file_id, caption=text, reply_markup=markup,
                         parse_mode=ParseMode.HTML)
    await state.set_state("for_end")


async def cancel_file(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get('lang')
    if lang == 'uz':
        text = f"<b>Kimdan: </b> {data.get('name')}\n" \
               f"<b>Telefon raqami: </b> {data.get('phone')}\n" \
               f"<b>Foydalanuvchi nomi: </b> @{data.get('username')}\n" \
               f"<b>Murojaat turi: </b> {data.get('choose')}\n" \
               f"<b>Murojaat matni: </b> {data.get('main_text')}\n"
    else:
        text = f"<b>От кого: </b> {data.get('name')}\n" \
               f"<b>Номер телефона: </b> {data.get('phone')}\n" \
               f"<b>Имя пользователя: </b> @{data.get('username')}\n" \
               f"<b>Тип: </b> {data.get('choose')}\n" \
               f"<b>Текст: </b> {data.get('main_text')}\n"
    await state.update_data(body=text, file_name="")
    markup = await confirm_keyboard(data.get('lang'))
    await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=markup, parse_mode=ParseMode.HTML)
    await state.set_state("for_end")


async def finish(message: types.Message, state: FSMContext):
    message_text = message.text
    data = await state.get_data()
    body = data.get("body")
    lang = data.get("lang")
    call_data = ""
    if lang == "uz":
        if message_text == "✅ Murojaatni yuborish":
            call_data = "confirm"
        else:
            call_data = "cancel"
        text = "Sizning murojaatingiz qisqa muddatda ko'rib chiqiladi. Botni qayta ishga tushirish uchun /start yozing"
    else:
        if message_text == "✅ Отправить":
            call_data = "confirm"
        else:
            call_data = "cancel"
        text = "Ваше обращение будет рассмотрено в кратчайшее время. Введите /start, чтобы перезапустить бот"
    file_type = data.get("file_type")
    file_name = data.get("file_name")
    if call_data == 'confirm':
        await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=types.ReplyKeyboardRemove())
        sender_address = config('SENDER_ADDRESS')
        sender_pass = config('SENDER_PASSWORD')
        receiver_address = config('RECEIVER_ADDRESS')
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = 'Yangi murojaat'
        message.attach(MIMEText(body, 'html'))
        if file_name != "":
            if file_type == "only":
                file = MIMEApplication(open(f"files/{file_name}", 'rb').read())
                file.add_header('Content-Disposition', 'attachment', filename=file_name)
                message.attach(file)
            else:
                files = file_name.split("=+=")
        session = smtplib.SMTP('mail.uzbektourism.uz', 25, 'daac')
        # session.starttls()
        session.login(sender_address, sender_pass)
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()

    else:
        data = await state.get_data()
        lang = data.get("lang")
        if lang == "uz":
            text = "Tegishli fayllarni biriktiring (video, audio, tekst va boshqalar)"
        else:
            text = "Прикрепите соответствующие файлы (видео, аудио, текст и т. д.)"
        markup = await cancel_keyboard(lang)
        await bot.send_message(chat_id=message.from_user.id, text=text, reply_markup=markup)
        await state.set_state("main_file")


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(welcome, commands=['start', 'help'], state='*')
    dp.register_message_handler(privacy_agree, state='get_lang')
    dp.register_message_handler(choose, state='choose')
    dp.register_message_handler(choose_person_type, state='legal')
    dp.register_message_handler(get_appeal_type, state='appeal_type')
    dp.register_message_handler(get_phone_number, state='phone_number')
    dp.register_message_handler(get_location, state='location')
    dp.register_message_handler(get_phone_number_two, state='phone_number_two')
    dp.register_message_handler(get_text_from_user, state='text')
    dp.register_message_handler(main_file_text, state='main_file_text')
    dp.register_message_handler(main_document, state='main_file', content_types=types.ContentType.DOCUMENT)
    dp.register_message_handler(main_photo, state='main_file', content_types=types.ContentType.PHOTO)
    dp.register_message_handler(main_video, state='main_file', content_types=types.ContentType.VIDEO)
    dp.register_message_handler(main_audio_voice, state='main_file', content_types=types.ContentType.VOICE)
    dp.register_message_handler(main_audio_voice, state='main_file', content_types=types.ContentType.AUDIO)
    dp.register_message_handler(cancel_file, state='main_file', content_types=types.ContentType.TEXT)
    dp.register_message_handler(finish, state='for_end')
