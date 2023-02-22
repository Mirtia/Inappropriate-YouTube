/**
 * Author : Myrsini Gkolemi
 * Date : 20/02/2021
 * Description : Functions to scrap YouTube channel information from About Tab.
 */

const puppeteer = require('puppeteer');
const fs = require('fs');

/**
 * Get mails of channels in list and append to file.
 * @param {string[]} channelList 
 * @param {string} dstFile 
 */
const getMails = async (channelList, dstFile) => {
    const browser = await puppeteer.launch({
        headlesss: true,
        defaultViewport: null,
        args: ['--window-size=1920,3000']
    });

    var mailAddress = false;
    const userAgent = '5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36';

    for (let i = 0; i < channelList.length; i++) {
        const page = await browser.newPage();
        await page.setUserAgent(userAgent);

        try {
            await page.goto("https://www.youtube.com/channel/" + channelList[i] + "/about", { waitUntil: 'load', timeout: 0 });
            if (i == 0) {
                await page.click('button[aria-label="Agree to the use of cookies and other data for the purposes described"]');
            }
            try {
                await page.waitForSelector("#details-container > table > tbody > tr:nth-child(1) > td:nth-child(2) > yt-formatted-string > a", { timeout: 5000 });
                mailAddress = await page.evaluate(
                    () => {
                        var email = document.querySelector("#details-container > table > tbody > tr:nth-child(1) > td:nth-child(2) > yt-formatted-string > a");
                        return new Boolean(email).valueOf();
                    });
            } catch (error) {
                mailAddress = false;
                console.log(error.message);
                // await page.screenshot({path : i + "_state.png"});                
            }
            await appenMail(dstFile, mailAddress, channelList[i], "mail");
        }
        catch (error) {
            // Channel terminated
            console.log("Warning: Page cannot be reached.");
            await page.screenshot({ path: i + "_fatal.png" });
            console.log(error.message);
        }
        await page.close();
    }
    await browser.close();
};

/**
 * Read channel ids from file (format: 1 id/per line)
 * @param {string} srcFile 
 * @returns 
 */
const readIds = async (srcFile) => {
    const fileData = fs.readFileSync(srcFile);
    return JSON.parse(fileData).map((object) => object["id"]);
};

/**
 * Rewrite destination file by appending new mail response.
 * @param {string} dstFile 
 * @param {object} mail 
 * @param {string} id 
 * @param {string} type 
 */
const appenMail = async (dstFile, mail, id, type) => {
    fs.readFile(dstFile, (err, data) => {
        if (err) return console.log(err);
        let jsonData = JSON.parse(data);
        jsonData.push({ "id": id, type: mail });

        fs.writeFile(dstFile,
            "[" + jsonData.map((jsonObject) => JSON.stringify(jsonObject) + "\n") + "]",
            function (err, data) {
                if (err) return console.log(err);
                // console.log(jsonData);
            });
    });
};

(async () => {
    const srcFile = process.argv[2];
    const dstFile = process.argv[3];
    // console.log("Source file name: ", srcFile);      
    const channelList = await readIds(srcFile);
    await getMails(channelList, dstFile);
})();

// The following functions are not implemented.

/**
 * Get links associated with the channels in list.
 * @param {string} channelId 
 */
const getLinks = async (channelId) => {
    // socialMedia = await page.evaluate ( 
    //     () => {
    //         var linkContainers = Array.from(document.querySelectorAll("#link-list-container > a"));
    //         return linkContainers.map(element =>  { return {"text": element.innerText, "href": decodeURIComponent(element.href)};});
    //     } );
    throw { name: "NotImplementedError", message: "This function is not implemented." };
};
