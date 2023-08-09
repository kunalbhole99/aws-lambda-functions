import boto3
import csv
import os

# Initialize AWS clients
s3_client = boto3.client('s3')
ec2_client = boto3.client('ec2')

# Define the S3 bucket and file name
s3_bucket = os.environ['s3_bucket']
s3_file_key = os.environ['s3_file_key']

# Define the NACL ID
nacl_id = os.environ['nacl_id']

def get_next_available_rule_number(existing_entries):
    rule_numbers = {int(entry['RuleNumber']) for entry in existing_entries}
    available_numbers = set(range(1, 32767)) - rule_numbers
    return min(available_numbers) if available_numbers else None


def lambda_handler(event, context):
    try:
        # Download the CSV file from S3
        temp_csv_path = '/tmp/SOC_malicious_ip.csv'
        s3_client.download_file(s3_bucket, s3_file_key, temp_csv_path)
        
        # Process CSV and extract malicious IPs
        malicious_ips = set()
        with open(temp_csv_path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)  # Skip the header row
            for row in csv_reader:
                if len(row) >= 1:
                    ip_address = row[0].strip()  # Remove leading/trailing whitespaces
                    malicious_ips.add(ip_address)
        
        # Get existing NACL entries
        existing_nacls = ec2_client.describe_network_acls(NetworkAclIds=[nacl_id])
        existing_entries = existing_nacls['NetworkAcls'][0]['Entries']
        
        # Determine new IPs to add
        existing_ips = {entry['CidrBlock'].split('/')[0] for entry in existing_entries}
        new_ips_to_add = malicious_ips - existing_ips
        
        print("malicious ips", malicious_ips)
        print("existing block ips", existing_ips)
        print("ips need to block", new_ips_to_add)
        
        next_rule_number = get_next_available_rule_number(existing_entries)
        blocked_ips = []
        # Update NACL to block new malicious IPs
        for ip in new_ips_to_add:
            
            print(f"rule number for: {ip} is {next_rule_number}")
            if next_rule_number is not None:
                print(f"Adding rule for IP: {ip}")
                try:
                    ec2_client.create_network_acl_entry(
                        NetworkAclId=nacl_id,
                        RuleNumber=next_rule_number,
                        Protocol='-1',
                        RuleAction='deny',
                        Egress=False,
                        CidrBlock=f'{ip}/32'
                    )
                    blocked_ips.append(ip)
                    print(f"Blocked IP: {ip}")
                    
                    next_rule_number += 1
                    
                    print(f"next rule number: {next_rule_number}")
                    
                except Exception as e:
                    print(f"Error adding rule for IP {ip}: {str(e)}")
                    
                
                    
            else:
                print("No available rule number for IP: {ip}")
                
                blocked_ips.append(ip)
                print(f"Blocked IP: {ip}")
        
        # Clean up temp file
        os.remove(temp_csv_path)
        
        if blocked_ips:
            confirmation_message = f"Blocked {len(blocked_ips)} malicious IPs: {', '.join(blocked_ips)}"
            print(confirmation_message)
        else:
            confirmation_message = "No new malicious IPs to block."
            print(confirmation_message)
            
        return {
            'statusCode': 200,
            'body': 'Malicious IPs blocked successfully'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error: {str(e)}'
        }
