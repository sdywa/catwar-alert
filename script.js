// ==UserScript==
// @name         CatwarAlert
// @version      0.2
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
    const MAX_STRING_LIMIT = 240;
    const DEFAULT_URL = `http://localhost:${PORT}/test`;

    function sliceURI(URI, start=0, end=MAX_STRING_LIMIT)
    {
        let sliced = URI.slice(start, end);
        let encoded;
        try
        {
            encoded = decodeURI(sliced);
        }
        catch (URIError)
        {
            [encoded, end] = sliceURI(URI, start, end - 1);
        }
        return [encoded, end]
    }

    async function sendContent(content, type='system', kwargs={}) {
        const INFO_URL = new URL(DEFAULT_URL);
        INFO_URL.searchParams.set('type', type);
        for (const keyword in kwargs)
            INFO_URL.searchParams.set(keyword, kwargs[keyword]);
        await fetch(INFO_URL);

        const ENCODED_CONTENT = encodeURI(content);
        let isEnd = false;
        let index = 0;
        while (!isEnd)
        {
            const CONTENT_URL = new URL(DEFAULT_URL);
            let [text, end] = sliceURI(ENCODED_CONTENT, index, index+MAX_STRING_LIMIT)
            if (end > ENCODED_CONTENT.length)
                isEnd = true;

            CONTENT_URL.searchParams.set('end', + isEnd);
            for (const keyword in kwargs)
                CONTENT_URL.searchParams.set(keyword, kwargs[keyword]);
            CONTENT_URL.searchParams.set('content', text);
            await fetch(CONTENT_URL);

            index = end;
        }
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
        const text = `${ formatMessage(message) }`;
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
