// ==UserScript==
// @name         CatwarAlert
// @version      0.1
// @description  Скрипт, передающий информацию серверу
// @author       Ale
// @match        https://catwar.su/*
// @grant        none
// ==/UserScript==

const socket = window.socket;

(function() {
    'use strict';
    /* eslint-disable curly, no-return-assign */
    const HOST = 'localhost';
    const PORT = 12345;
    const MESSAGES = [];

    function sendContent(content, type='system', kwargs={}) {
         const XHTTP = new XMLHttpRequest();
         const MY_URL = new URL(`http://localhost:${PORT}/test`);
         MY_URL.searchParams.set('type', type);
         MY_URL.searchParams.set('content', content);
         for (const keyword in kwargs)
             MY_URL.searchParams.set(keyword, kwargs[keyword]);
         XHTTP.open('GET', MY_URL);
         XHTTP.send();
     }

    function formatMessage(message) {
        return `${ message.text } — ${ message.login } [${ message.cat }]`;
    }

    function formatTime(time) {
        const date = new Date(time * 1000);
        return `${ date.toLocaleDateString("ru-RU", { day: 'numeric', month: 'long' }) } в ${ date.toLocaleTimeString("ru-RU", {hour: "numeric", minute: "numeric"}) }`;
    }

    function sendRecentMessages(messages) {
        for (const message of messages) {
            const text = `Старое сообщение от ${ formatTime(message.time) }:\n${ formatMessage(message) }`;
            if (!MESSAGES.includes(message.id)) {
                MESSAGES.push(message.id);
                sendContent(text, 'chat', { id: message.id });
            }
        }
    }

    function alertAboutMessage(count) {
        if (count > 0)
            sendContent('У вас новое личное сообщение!');
    }

    function sendMessage(message) {
        const text = `${ formatMessage(message) }`;
        MESSAGES.push(message.id);
        sendContent(text, 'chat', { id: message.id });
    }

    socket.on('msg load', sendRecentMessages);
    socket.on('msg', sendMessage);
    socket.on('notRead mess', alertAboutMessage);
})();