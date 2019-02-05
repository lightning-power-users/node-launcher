import time

from grpc._channel import _Rendezvous

from node_launcher.node_set.lnd_client.rpc_pb2 import OpenStatusUpdate
from tools.lnd_client import lnd_client
from tools.secrets import spreadsheet_id


def get_google_sheet_data(node_operator):
    from googleapiclient.discovery import build
    from httplib2 import Http
    from oauth2client import file, client, tools
    SCOPES = 'https://www.googleapis.com/auth/spreadsheets'

    SAMPLE_RANGE_NAME = 'Form Responses 1!A1:J'
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage('token.json')
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        credentials = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=credentials.authorize(Http()))

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range=SAMPLE_RANGE_NAME).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        total = 0
        for index, row in enumerate(values[1:]):
            old_row = row[3:]
            pubkey = row[1].split('@')[0]
            # twitter_handle = row.get(2)
            if pubkey in node_operator.nodes:
                node = node_operator.nodes[pubkey]
                txids = [c.channel_point for c in node.channels]
                new_row = [
                    len(node.channels),
                    node.remote_balance,
                    node.local_balance,
                    node.available_capacity,
                    node.balance,
                    ', '.join(txids)
                ]
                status = ''
                if len(node.channels) == 1 and node.remote_balance:
                    total += node.capacity
                    print(node.pubkey, "{0:,d}".format(node.capacity))
                    response = lnd_client.open_channel(
                        node_pubkey_string=node.pubkey,
                        local_funding_amount=max(node.capacity, 200000),
                        push_sat=0,
                        sat_per_byte=1,
                        spend_unconfirmed=True
                    )
                    try:
                        for update in response:
                            if isinstance(update, OpenStatusUpdate):
                                print(update)
                                status = 'Pending channel'
                                break
                            else:
                                print(update)
                    except _Rendezvous as e:
                        status = e.details()
                new_row.append(status)
            else:
                new_row = [
                    0,
                    0,
                    0,
                    0,
                    0,
                    ''
                ]
            changed = False
            for i, _ in enumerate(new_row[:-2]):
                try:
                    if old_row[i] == '':
                        old_row[i] = 0
                    old_value = int(float(str(old_row[i]).replace(',', '')))
                except IndexError:
                    old_value = 0

                if new_row[i] is not None and int(new_row[i]) != old_value:
                    changed = True
                    break
            if changed or True:
                body = dict(values=[new_row])
                try:
                    result = service.spreadsheets().values().update(
                        spreadsheetId=spreadsheet_id,
                        range=f'Form Responses 1!D{index + 2}:J',
                        body=body,
                        valueInputOption='USER_ENTERED').execute()
                    time.sleep(0.5)
                except Exception as e:
                    pass
