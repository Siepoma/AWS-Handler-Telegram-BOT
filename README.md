# AWS-Handler-Telegram-BOT
A telegram bot to perform simple task on your amazon ec2


### Telegram
1. Go to [Telegram Web](https://web.telegram.org/).
2. Start a chat with [@BotFather](https://telegram.me/BotFather).
3. Type "/start".
4. Type "/newbot" to create a new bot. I named my bot "lesterchan_bot".
5. Note the HTTP API access token that @BotFather will reply you after you created the bot.

### AWS Lambda
1. Go to [AWS Lambda]
2. Click "Get Started Now".
3. Click "Author from scratch".
4. Give your function a name, choose Python3.6
5. Under "Role",  choose "Create a new role from templates".
6. Under "Policy templates", choose "Basic Lambda @ Edge permissions"
7. Click "Create function".

### AWS API Gateway
1. Go to [AWS API Gateway]
2. Click "Get Started Now".
3. Under "API name", enter the name of your API. E.G. "Telegram Bot".
4. Click "Create API".
5. You will be redirected to the "Resources" page.
6. Click "Create Method" and on the dropdown menu on the left, choose "ANY".
7. Under "Integration Type", choose "Lambda Function".
8. Tick "Use Lambda Proxy integration".
9. Under "Lambda Function", choose the name of your function.
10. Click "Save" and "Ok" when the popup appears.
11. You will be brought to the "/ - ANY - Method Execution" Page. Test your API.
12. Click on "Action/Deploy API" button on the top left.
13. Under "Deployment Stage", click "New Stage".
14. Under "Stage Name", type "v1".
15. Click "Deploy".
16. Note the "Invoke URL" at the top and your API is now live. Save it.

### Set Telegram Webhook
1. Replace &lt;BOT-TOKEN&gt; with your Telegram HTTP API access token obtained in the first step. 
2. Replace &lt;API-URL&gt; with your Invoke URL obtained in the previous step.
3. From any browser go to: https://api.telegram.org/bot<BOT-TOKEN>/setWebHook?url=<API-URL>:

You should obtain something like this:
```
{"ok":true,"result":true,"description":"Webhook was set"}
```

### AWS IAM
1. Go to [IAM]
2. Click "Role"
3. Click on your bot Role, you should be able to recognize it from the name
4. Under Authorization click "Add Ppermissions"
5. Filter and add the policy you want to give to your bot, I gave "AmazonEC2FullAccess"
### Testing via Telegram
1. Message your Telegram Bot that you have created.
2. Send help.
3. You should get back the list of possible command
