# catwar-alert
Utility for transmitting game state from browser to Telegram.
## Prerequisites
Before you begin, ensure that you have the following prerequisites:
- [Git](https://git-scm.com/downloads)
- [Python](https://www.python.org/downloads) (version 3.10 or later)
- [Tampermonkey](https://www.tampermonkey.net/index.php) browser extension installed for your browser
## Installation
Before installing the Tampermonkey script, ensure that you have the Tampermonkey browser extension installed in your browser.

### 1. Clone the Repository
Open a terminal or command prompt and clone the repository using the following command:
```bash
git clone https://github.com/sdywa/catwar-alert.git
```

### 2. Install Dependencies
Navigate to the cloned repository folder and install the necessary dependencies, using the following commands:
```bash
cd catwar-alert
pip install -r requirements.txt
```

### 3. Add the Script
Click on the Tampermonkey extension icon in the toolbar and select "Create a new script". Open the `script.js` file in the repository and copy the entire script code. Paste the copied code into the Tampermonkey script editor and save it.

### 4. Enable the Script
Make sure the script is enabled by checking the checkbox next to its name in the Tampermonkey extension menu.

### 5. Run the Python Script
Execute the following command in the repository folder:
```bash
python main.py
```

### 6. Configure the Script
After successfully running the script, enter the token of your Telegram bot and select the default value for the chat ID.

To obtain the chat ID, write a message to your Telegram bot. You will receive a response that looks similar to the following image:

![Response](https://github.com/sdywa/catwar-alert/assets/73535285/631fc0ce-35b3-4215-a180-a470beb1577e)

Restart the Python script and enter the retrieved chat ID.
