const BOT_TOKEN = '8811277023:AAH_1iBPjb-dlmPDWc1vwMCPQEITzLuWDec';
const ANKETA_UZ = 'https://yakubovibrohim.github.io/MBI_anketa/mebel_anketa.html';
const ANKETA_RU = 'https://yakubovibrohim.github.io/MBI_anketa/mebel_anketa_ru.html';
const ADMIN_CHAT_ID = '1487569442';

function doPost(e) {
  try {
    const upd = JSON.parse(e.postData.contents);

    // Callback query — tugma bosildi
    if (upd.callback_query) {
      const callbackId = upd.callback_query.id;
      const chatId = upd.callback_query.message.chat.id;
      const ism = upd.callback_query.from.first_name || 'Mijoz';
      const data = upd.callback_query.data;

      // Callback ni tasdiqlash
      UrlFetchApp.fetch('https://api.telegram.org/bot' + BOT_TOKEN + '/answerCallbackQuery', {
        method: 'post',
        contentType: 'application/json',
        payload: JSON.stringify({ callback_query_id: callbackId }),
        muteHttpExceptions: true
      });

      if (data === 'til_uz') {
        sendMsg(chatId,
          'Assalomu alaykum, ' + ism + '! 👋\n\n' +
          '🪑 MEBEL BY IBROHIM ga xush kelibsiz!\n\n' +
          'Buyurtma berish uchun anketani toldiring:\n' +
          '👇👇👇\n\n' + ANKETA_UZ + '\n\n' +
          'Anketani toldirgach ustamiz siz bilan boglanadi! ✅'
        );
        Utilities.sleep(1500);
        sendMsg(chatId,
          '📎 Sizda loyiha rasmi, xona surati yoki PDF fayl bormi?\n\n' +
          'Bor bolsa — shu yerga yuboring 👆\n' +
          'Yoq bolsa — havotir olmang 😊'
        );
      }

      if (data === 'til_ru') {
        sendMsg(chatId,
          'Здравствуйте, ' + ism + '! 👋\n\n' +
          '🪑 Добро пожаловать в MEBEL BY IBROHIM!\n\n' +
          'Для заказа мебели заполните анкету:\n' +
          '👇👇👇\n\n' + ANKETA_RU + '\n\n' +
          'После заполнения наш мастер свяжется с вами! ✅'
        );
        Utilities.sleep(1500);
        sendMsg(chatId,
          '📎 У вас есть файл проекта, фото комнаты или PDF?\n\n' +
          'Если есть — отправьте сюда 👆\n' +
          'Если нет — не беспокойтесь 😊'
        );
      }

      return ok();
    }

    if (!upd.message) return ok();

    const cache = CacheService.getScriptCache();
    const ckey = 'upd_' + upd.update_id;
    if (cache.get(ckey)) return ok();
    cache.put(ckey, '1', 3600);

    const chatId = upd.message.chat.id;
    const ism = upd.message.from.first_name || 'Mijoz';
    const username = upd.message.from.username ? '@' + upd.message.from.username : 'username yoq';
    const text = upd.message.text || '';

    if (text === '/start') {
      sendButtons(chatId,
        '🪑 MEBEL BY IBROHIM\n\nIltimos tilni tanlang / Пожалуйста выберите язык:',
        [
          [{ text: "🇺🇿 O'zbek tili", callback_data: "til_uz" }],
          [{ text: "🇷🇺 Русский язык", callback_data: "til_ru" }]
        ]
      );
      return ok();
    }

    if (upd.message.photo || upd.message.document) {
      sendMsg(ADMIN_CHAT_ID,
        '📎 Yangi fayl/rasm!\n👤 ' + ism + ' (' + username + ')\n📱 ' + chatId
      );
      UrlFetchApp.fetch('https://api.telegram.org/bot' + BOT_TOKEN + '/forwardMessage', {
        method: 'post',
        contentType: 'application/json',
        payload: JSON.stringify({
          chat_id: ADMIN_CHAT_ID,
          from_chat_id: chatId,
          message_id: upd.message.message_id
        }),
        muteHttpExceptions: true
      });
      sendMsg(chatId, '✅ Rahmat! Faylingiz qabul qilindi.\n\nUstamiz boglanadi.\n📞 +998 91 135 44 66');
    }

  } catch(err) {
    Logger.log('Xatolik: ' + err);
  }
  return ok();
}

function sendMsg(chatId, text) {
  UrlFetchApp.fetch('https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage', {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({ chat_id: chatId, text: text }),
    muteHttpExceptions: true
  });
}

function sendButtons(chatId, text, buttons) {
  UrlFetchApp.fetch('https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage', {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({
      chat_id: chatId,
      text: text,
      reply_markup: { inline_keyboard: buttons }
    }),
    muteHttpExceptions: true
  });
}

function ok() {
  return ContentService.createTextOutput('OK');
}

function setWebhook() {
  var scriptUrl = 'https://script.google.com/macros/s/AKfycbwFxn2q8FYVVASIXJkobkAekQcA-AsZWHrvEFeNP11jVF3u5mFtJ4yPM06i41BKmT6u/exec';
  var res = UrlFetchApp.fetch(
    'https://api.telegram.org/bot' + BOT_TOKEN +
    '/setWebhook?url=' + scriptUrl + '&drop_pending_updates=true&max_connections=1'
  );
  Logger.log(res.getContentText());
}
