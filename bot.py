import json
from botocore.vendored import requests
from datetime import datetime, timedelta
import boto3
import traceback
import time
ec2 = boto3.resource('ec2')
client = boto3.client('ec2')

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
    send_message(texto, chat_id)





    
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

    
	
def backup(chat_id,iName):
    '''This method searches for all EC2 instances and create a backup of the one with the name passed
    '''
	
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
            instance_id = instance.id.lower()
            print('Instance Found')
            break
    
		
    created_on = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    nameImg = 'noName'
    images = client.describe_images(Filters=[{'Name': 'tag:nameEc2', 'Values': [name]}])
    print(images)
    for image_data in images['Images']:
        image = ec2.Image(image_data['ImageId'])
        name_tag = [tag['Value'] for tag in image.tags if tag['Key'] == 'Name']
        if name_tag:
            print(f"Deregistering {name_tag[0]}")
        image.deregister()
    
    if(instance_id):
        nameImg = f"InstanceId({instance_id})_CreatedOn({created_on})"
        print(f"Creating Backup: {nameImg}")
        image_description = client.create_image(InstanceId=instance_id, Name=nameImg)
        image = ec2.Image(image_description['ImageId'])
        image.create_tags(Tags=[{'Key': 'nameEc2', 'Value': name}, {'Key': 'Name', 'Value': nameImg}])    

			
    if(final_text == '1'):
        final_text = "Your ec2 " + iName +" is back up is going...\n Image Name: " + nameImg
    else:
        final_text = "Sorry man, I couldn't find your Ec2 instance... =("
    url = URL + "sendMessage?text={}&chat_id={}".format(final_text, chat_id)
    requests.get(url)    

def terminate(chat_id,iName):
    '''STEP A: This method searches for all EC2 instances and create a backup of the one with the name passed
    '''
	
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
            instance_id = instance.id.lower()
            instanceType = instance.instance_type
            securityGroups = instance.security_groups
            for sGroup in securityGroups:
                securityGroupsIds =  (sGroup['GroupId']) 
            print('Instance Found')
            break
    
		
    created_on = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    nameImg = 'noName'
    
    ''' STEP B: Look all Images that cannot be removed and remove it
    '''
    images = client.describe_images(Filters=[{'Name': 'tag:nameEc2', 'Values': [name]},{'Name': 'tag:Removable', 'Values': ['False']}])
    oldImageIds = []
    for image_data in images['Images']:
        oldImageIds.append(image_data['ImageId'])
    
    ''' STEP C: Look all Images that came from the same Instance and that can be removed and remove it
    '''
    
    images = client.describe_images(Filters=[{'Name': 'tag:nameEc2', 'Values': [name]},{'Name': 'tag:Removable', 'Values': ['True']}])
    print(images)
    for image_data in images['Images']:
        image = ec2.Image(image_data['ImageId'])
        name_tag = [tag['Value'] for tag in image.tags if tag['Key'] == 'Name']
        ebses = image_data['BlockDeviceMappings']
        SnapIDs = []
        for ebs in ebses:
            SnapIDs.append(ebs['Ebs']['SnapshotId'])
        if name_tag:
            print(f"Deregistering {name_tag[0]}")
        image.deregister()
        for SnapID in SnapIDs:
            client.delete_snapshot(SnapshotId=SnapID)
    
    ''' STEP D: BACKUP
    '''
            
    if(instance_id):
        nameImg = f"InstanceId({instance_id})_CreatedOn({created_on})"
        print(f"Creating Backup: {nameImg}")
        image_description = client.create_image(InstanceId=instance_id, Name=nameImg)
        image = ec2.Image(image_description['ImageId'])
        image.create_tags(Tags=[{'Key': 'nameEc2', 'Value': name}, {'Key': 'Name', 'Value': nameImg},{'Key': 'Removable', 'Value': 'False'},{'Key': 'SecurityGroupsIds', 'Value': securityGroupsIds},{'Key': 'InstanceType', 'Value': instanceType}])
        
        status = image.state
        count = 1
        print(f"State: {status}")
        while status == 'pending' and count < 50:
                time.sleep(6)
                count += 1
                image = ec2.Image(image_description['ImageId'])
                status = image.state
                print(f"State : {status}")
                msg = 'Backing up the image: ' + nameImg + ' status : ' + status
                url = URL + "sendMessage?text={}&chat_id={}".format(msg, chat_id)
                requests.get(url)
                
                
        
        instancesTeminated = client.terminate_instances(InstanceIds=[instance_id])
        print(f"Instance State Backup: {instancesTeminated['TerminatingInstances']}")
        
    ''' STEP E: BACKUP
    '''
    for id in oldImageIds:
        if id:
            image = ec2.Image(id)
            image.create_tags(Tags=[{'Key': 'Removable', 'Value': 'True'}])

    ''' STEP F: RISP
    '''
    
    if(final_text == '1'):
        final_text = "Your ec2 " + iName +" is terminating...\n Image Name: " + nameImg
    else:
        final_text = "Sorry man, I couldn't find your Ec2 instance... =("
    url = URL + "sendMessage?text={}&chat_id={}".format(final_text, chat_id)
    requests.get(url)    

    
def runInstance(chat_id,imageId):
    '''This method start instance from img
    '''
    final_text = 0
    image = ec2.Image(imageId)
    
    if image.image_id:
        securityGroupsIds = [tag['Value'] for tag in image.tags if tag['Key'] == 'SecurityGroupsIds']
        IType = [tag['Value'] for tag in image.tags if tag['Key'] == 'InstanceType']
        nameEc2 = [tag['Value'] for tag in image.tags if tag['Key'] == 'nameEc2']
        print(f"   {imageId} --   {securityGroupsIds}")
        try:
            instanceInfo = client.run_instances(ImageId=imageId,InstanceType=IType[0],SecurityGroupIds=securityGroupsIds,MaxCount=1,MinCount=1)
            print(f"   {instanceInfo} ")
            final_text = '1'
            ID = instanceInfo['Instances'][0]['InstanceId']
            
            instance = ec2.Instance(ID)
            status = instance.state['Name']
            count = 1
            while status == 'pending' and count < 60:
                count += 1
                time.sleep(10)
                instance = ec2.Instance(ID)
                status = instance.state['Name']
                
            if status == 'running':
                instance.create_tags(Tags=[{'Key': 'Name', 'Value': nameEc2[0]}])
            else:
                print('Instance status: ' + status)

            
        except Exception as e:
                raise e 
        
	
    if(final_text == '1'):
        final_text = "Your ec2 is starting... pls wait" 
    else:
        final_text = "Sorry man, I couldn't find your Ec2 instance... =("
    
    url = URL + "sendMessage?text={}&chat_id={}".format(final_text, chat_id)
    requests.get(url)		

def ec2Images(chat_id):
    
    filters = [
        {
            'Name': 'tag:Removable',
            'Values': ['False']
        }
    ]
    
    images = client.describe_images(Filters = filters)
    
    images_info = '\n'
    for image_data in images['Images']:
        tags = image_data['Tags']
        tags = tags or []
        names = [tag.get('Value') for tag in tags if tag.get('Key') == 'Name']
        name = names[0] if names else None
        namesEc2 = [tag.get('Value') for tag in tags if tag.get('Key') == 'nameEc2']
        nameEc2 = namesEc2[0] if namesEc2 else None
        image_info = image_data['ImageId'] + ' - ' + name + ' - ' + nameEc2
        images_info = images_info + image_info + '\n'
    
    url = URL + "sendMessage?text={}&chat_id={}".format(images_info, chat_id)
    requests.get(url)

def test(job_id,chat_id):
    print('test before')
    text = 'Msg 1 - ' + str(job_id)
    url = URL + "sendMessage?text={}&chat_id={}".format(text , chat_id)
    requests.get(url)
    count = 2
    while count < 8:
        time.sleep(1)
        text = 'Msg ' + str(count) + ' - ' + str(job_id)
        print('Test after')
        url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
        requests.get(url)
        count += 1

    
def lambda_handler(event, context):
    job_id = None
    print(event)
    try:
        
        job_id = event['update_id']
        print('EVENT: ' + json.dumps(event))
        try:
            message = event['message']
        except:
            message = event['edited_message']
        

        chat_id = message['chat']['id']

        
        try:
            senderUsr = message['from']['username']
        except:
            try:
                senderUsr = message['from']['first_name']
            except:
                senderUsr = 'NoOne'
        try:
            reply = message['text']
        except Exception as e:
            try:
                reply = message['new_chat_member']
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
        elif (op[0].lower() == 'list_img'):
            ec2Images(chat_id)
        elif (op[0].lower() == 'backup'):
            backup(chat_id, params[0].strip())
        elif (op[0].lower() == 'test'):
            test(job_id,chat_id)
        elif (op[0].lower() == 'run_instance'):
            runInstance(chat_id, params[0].strip())
        elif (op[0].lower() == 'terminate'):
            print('call terminate with:' + params[0])
            terminate(chat_id, params[0].strip())
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
        chat_id = message['chat']['id']
        final_text = 'Ops, I had a problem... pls someone should check this REQ_ID: ' + context.aws_request_id
        url = URL + "sendMessage?text={}&chat_id={}".format(final_text, chat_id)
        requests.get(url)
        return {
            'statusCode': 200
        }
