// ==UserScript==
// @name         CatwarAlert
// @version      1.0
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
    const DEFAULT_URL = `http://${HOST}:${PORT}/test`;

    function prepareData(content) {
        const element = document.createElement('div');
        element.innerHTML = content;
        return JSON.stringify({'content': element.textContent});
    }

    async function sendContent(content, type='system', kwargs={}) {
        const INFO_URL = new URL(DEFAULT_URL);
        INFO_URL.searchParams.set('type', type);
        for (const keyword in kwargs)
            INFO_URL.searchParams.set(keyword, kwargs[keyword]);

        await fetch(INFO_URL, {
            method: 'POST',
            body: prepareData(content)
        });
    }

    function formatMessage(message) {
        return `${ message.text } — ${ message.login } [${ message.cat }]`;
    }

    function formatTime(time) {
        const date = new Date(time * 1000);
        return `${ date.toLocaleDateString("ru-RU", { day: 'numeric', month: 'long' }) } в ${ date.toLocaleTimeString("ru-RU", {hour: "numeric", minute: "numeric"}) }`;
    }

    async function sendRecentMessages(messages) {
        for (const message of messages) {
            const text = `Старое сообщение от ${ formatTime(message.time) }:\n${ formatMessage(message) }`;
            if (!MESSAGES.includes(message.id)) {
                MESSAGES.push(message.id);
                await sendContent(text, 'chat', { id: message.id });
            }
        }
    }

    async function alertAboutMessage(count) {
        if (count > 0)
            await sendContent('У вас новое личное сообщение!');
    }

    async function alertAboutChat(count) {
        if (count > 0)
            await sendContent('Вам написали в чат!');
    }

    async function alertAboutFight(data) {
        const ACTION = 27;
        if (data.dey == ACTION)
            await sendContent('Вы в боережиме!');
    }

    async function sendMessage(message) {
        const text = formatMessage(message);
        MESSAGES.push(message.id);
        await sendContent(text, 'chat', { id: message.id });
    }

    socket.on('msg load', sendRecentMessages);
    socket.on('msg', sendMessage);
    socket.on('notRead mess', alertAboutMessage);
    socket.on('notRead chat', alertAboutChat);
    socket.on('update', alertAboutFight);
    socket.on('pick', () => sendContent('Вас подняли!'));
})();
