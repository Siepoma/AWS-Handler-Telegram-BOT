import json
from botocore.vendored import requests
import boto3
import traceback
ec2 = boto3.resource('ec2')


TELE_TOKEN='<YOUR BOT TOKEN>'
URL = "https://api.telegram.org/bot{}/".format(TELE_TOKEN)
auth_usrs = [<AdminUsrName1>,<AdminUsrName2>]

def send_message(text, chat_id):
    final_text =  text
    url = URL + "sendMessage?text={}&chat_id={}".format(final_text, chat_id)
    requests.get(url)
    
def ec2Instances(chat_id):
    
    filters = [
        {
            'Name': 'instance-state-name',
            'Values': ['*']
        }
    ]
    
    instances = ec2.instances.filter(Filters = filters)
    
    instances_info = '\n'
    for instance in instances:
        tags = instance.tags
        tags = tags or []
        names = [tag.get('Value') for tag in tags if tag.get('Key') == 'Name']
        name = names[0] if names else None
        instance_info = instance.id + ' - ' + name + ' - ' + instance.state['Name']
        instances_info = instances_info + instance_info + '\n'
    
    url = URL + "sendMessage?text={}&chat_id={}".format(instances_info, chat_id)
    requests.get(url)

def getInstanceIp(chat_id,iName):
    filters = [
        {
            'Name': 'instance-state-name',
            'Values': ['*']
        }
    ]
    
    instances = ec2.instances.filter(Filters = filters)
    final_text = '-1'
    for instance in instances:
        tags = instance.tags
        tags = tags or []
        names = [tag.get('Value') for tag in tags if tag.get('Key') == 'Name']
        name = names[0] if names else None
        if ((name.lower() == iName.lower()) or (instance.id.lower() == iName.lower())):
            instanceFound = instance
            final_text = '1'
            print('Instance Found')
            break
    
    
    print(final_text)
    if(final_text == '1'):
        pubDNS = instanceFound.public_dns_name
        pubIP = instanceFound.public_ip_address
        if ( instanceFound.state['Name'] == 'running'  and pubIP is not None):
            final_text = iName + ' IP: ' + pubIP + ' DNS: ' + pubDNS
            print(final_text)
        else:
            final_text = iName + ' not running right now, try start command'
        
    else:
        final_text = iName + ' not found, maybe misspelled?'
    
    url = URL + "sendMessage?text={}&chat_id={}".format(final_text, chat_id)
    requests.get(url)
    


def help(chat_id):
    texto = 'Commands available:\n Start:(<Instance-Name or ID>) ---> Start specified Instance \n Stop:(<Instance-Name or ID>) ---> Stop specified Instance \n List ---> Show all available instances \n GetIp:(<Instance-Name or ID>) ---> Return public Ip and Host of the specified Instance'
    url = URL + "sendMessage?text={}&chat_id={}".format(texto, chat_id)
    requests.get(url)




    
def startEc2(chat_id, iName):
    filters = [
        {
            'Name': 'instance-state-name',
            'Values': ['*']
        }
    ]
    
    instances = ec2.instances.filter(Filters = filters)
    final_text = '-1'
    for instance in instances:
        tags = instance.tags
        tags = tags or []
        names = [tag.get('Value') for tag in tags if tag.get('Key') == 'Name']
        name = names[0] if names else None
        if ((name.lower() == iName.lower()) or (instance.id.lower() == iName.lower())):
            instanceFound = instance
            final_text = '1'
            print('Instance Found')
            break
    
    if(final_text != '-1' and instanceFound.state['Name'] == 'stopped'):
        instanceFound.start()
        final_text = "Your ec2 " + iName +" is starting..."
    else:
        final_text = "Sorry man, I couldn't find your Ec2 instance... =("
    url = URL + "sendMessage?text={}&chat_id={}".format(final_text, chat_id)
    requests.get(url)
    
def stopEc2(chat_id, iName):
    filters = [
        {
            'Name': 'instance-state-name',
            'Values': ['*']
        }
    ]
    
    instances = ec2.instances.filter(Filters = filters)
    final_text = '-1'
    for instance in instances:
        tags = instance.tags
        tags = tags or []
        names = [tag.get('Value') for tag in tags if tag.get('Key') == 'Name']
        name = names[0] if names else None
        if ((name.lower() == iName.lower()) or (instance.id.lower() == iName.lower())):
            instanceFound = instance
            final_text = '1'
            print('Instance Found')
            break
    
    if(final_text != '-1' and instanceFound.state['Name'] == 'running'):
        instanceFound.stop()
        final_text = "Your ec2 " + iName +" is stoppig..."
    else:
        final_text = "Sorry man, I couldn't find your Ec2 instance... =("
    url = URL + "sendMessage?text={}&chat_id={}".format(final_text, chat_id)
    requests.get(url)    

    
    
def lambda_handler(event, context):
    try:
        message = json.loads(event['body'])
        print('Context: ' + json.dumps(event))
        
        chat_id = message['message']['chat']['id']
        try:
            senderUsr = message['message']['from']['username']
        except:
            try:
                senderUsr = message['message']['from']['first_name']
            except:
                senderUsr = 'NoOne'
        try:
            reply = message['message']['text']
        except Exception as e:
            try:
                reply = message['message']['new_chat_member']
                send_message('Hi '+ senderUsr +'!\nWelcome to this magic group!\nTry the command help to find out all my capabilities',chat_id)
                return {
                    'statusCode': 200
                }
            except:
                raise e        
        
        usrsResp = '-'.join(auth_usrs)
        
        op = reply.split(":")
        if (len(op) > 1):
           params = op[1].split(",")
        
        if (op[0].lower() == 'help'):
            help(chat_id)
        elif (op[0].lower() == 'start'):
            if(senderUsr in auth_usrs):
                print('call start with:' + params[0])
                startEc2(chat_id, params[0].strip())
            else:
                send_message('Sorry dude you cannot perform this operation, pls ask to some of the follow users: ' + usrsResp, chat_id)
        elif (op[0].lower() == 'stop'):
            if(senderUsr in auth_usrs):
                print('call stop with:' + params[0])
                stopEc2(chat_id, params[0].strip())
            else:
                send_message('Sorry dude you cannot perform this operation, pls ask to some of the follow users: ' + usrsResp, chat_id)
        elif (op[0].lower() == 'list'):
            ec2Instances(chat_id)
        elif (op[0].lower() == 'getip'):
            print('call getip with:' + params[0])
            getInstanceIp(chat_id, params[0].strip())
        else:
            send_message('Sorry but I don\'t know what to do with your request, try help to find out my capabilities ;) ', chat_id)
        return {
            'statusCode': 200
        }
    except:
        print('####ERROR####\n')
        traceback.print_exc()
        chat_id = message['message']['chat']['id']
        final_text = 'Ops, I had a problem... pls someone should check this REQ_ID: ' + context.aws_request_id
        url = URL + "sendMessage?text={}&chat_id={}".format(final_text, chat_id)
        requests.get(url)
        return {
            'statusCode': 200
        }
