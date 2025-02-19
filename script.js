// ==UserScript==
// @name         CatwarAlert
// @version      1.1
// @description  Скрипт, передающий информацию серверу
// @author       Ale
// @match        https://catwar.su/cw3*
// @match        https://catwar.net/cw3*
// @grant        none
// ==/UserScript==

const socket = window.socket;

(function() {
    'use strict';
    /* eslint-disable curly, no-return-assign */
    const HOST = 'localhost';
    const PORT = 20360;
    const MESSAGES = [];
    const DEFAULT_URL = `http://${HOST}:${PORT}/`;
    const MESSAGES_DEFAULT_URL = `http://${HOST}:${PORT + 1}/`;

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
        return `${ date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' }) } в ${ date.toLocaleTimeString('ru-RU', {hour: 'numeric', minute: 'numeric'}) }`;
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

    function getRandomRange(min, max) {
        return Math.random() * (max - min) + min;
    }

    function sleep(ms) {
        return new Promise((res) => setTimeout(() => {
            res();
        }, ms));
    }

    let eventSource;
    function setupSSEConnection(outerMessages=[]) {
        if (eventSource) {
            eventSource.close();
        }

        let messages = outerMessages;
        let isSending = false;
        eventSource = new EventSource(MESSAGES_DEFAULT_URL);

        eventSource.onmessage = async (event) => {
            if (event.data.trim() !== "") {
                messages.push(event.data);
            }

            if (!isSending) {
                while (messages.length) {
                    isSending = true;
                    document.querySelector("#text").value = messages[0];
                    document.querySelector("#msg_send").click();
                    messages = messages.slice(1);
                    await sleep(getRandomRange(1645, 2589));
                }

                isSending = false;
            }
        };

        eventSource.onerror = () => {
            eventSource.close();
            setTimeout(() => setupSSEConnection(messages), 2000);
        };
    }

    socket.on('msg load', sendRecentMessages);
    socket.on('msg', sendMessage);
    socket.on('notRead mess', alertAboutMessage);
    socket.on('notRead chat', alertAboutChat);
    socket.on('update', alertAboutFight);
    socket.on('pick', () => sendContent('Вас подняли!'));

    setupSSEConnection();
    window.addEventListener("beforeunload", () => {
        if (eventSource) {
            eventSource.close();
        }
    });
})();
