# Sisense BloX Database Writeback
This guide demonstrates setting up a simple BloX widget to enable front end users to write data back to the database. While this guide specifically uses AWS lambda to execute a SQL update statement, the general flow can be adapted depending on your setup and needs. 

In this guide, we are looking at an example use case of a sales person adding notes to an opportunity from Sisense.

## See it in action
![alt text](https://github.com/alexfrisbie/Sisense-BloX-DbWriteback/blob/main/writeback.gif "writeback gif")
*Note: This is a live connection with a refresh rate of 5 seconds to demonstrate the writeback*

# How it works
## Quick Implement
Follow these steps to create this BloX widget in your own environment:
1. Download the following files:
- BloxTemplate-DbWriteback.json
- BloxAction-DbWriteback.js
2. Create a widget type of BloX and upload a template [Tutorials](https://docs.sisense.com/main/SisenseLinux/sisense-blox-tutorials.htm) - See 'Exporting and Importing BloX Templates'
3. Create a custom action in Blox, copy the contents of BloxAction-DbWriteback.js into this action and make changes for your API. 

## Overview
The general flow that enables database writeback is as follows:
1. BloX widget contains an input field and submit button.
2. Submit button triggers a custom action, sending data from the input to a REST API.
3. REST API executes backend script to write data from input field to database. 
   - Note: Cloud Data Warehouses typically have APIs set up to accept SQL statements. These can be used in place of setting up your own REST API and backend service. 
5. Database security and schema set up appropriately to accept update statements from backend service.

## BloX
The BloX widget is composed of two parts, the JSON editor script and the JS action script.
- The JSON editor script defines the visual appearance of the widget, the input field and submit button, the data accessible to the action script, and when the action script is called. 
- The JS action script controls the interaction between Sisense and the REST API. Here we define the URL of the API along with the data we are sending. 

### Editor - JSON
The key components in the BloX editor to focus on are the input container and the submit button. The code snippets below contain the relevant components.

First, our input field is created with `"type": "Input.Text"` and we use `"id": "data.note"` to make the user input accessible from the back end.

```
{
    "type": "Container",
    "items": [
        {
            "spacing": "medium",
            "type": "TextBlock",
            "text": " ",
            "color": "black"
        },
        {
            "type": "Input.Text",
            "id": "data.note",
            "placeholder": "Update project notes...",
            "isMultiline": true,
            "rows": "4",
            "borderRadius": "8px",
            "borderStyle": "none",
            "backgroundColor": "#F4F4F8"
        }
    ]
}
```

Next, we use an ActionSet to create a submit button. We define which custom action is used with `"type": "updateDb"` - this indicates the custom action with the name updateDb will trigger when the button is clicked. Additionally, we have `"data": {"id": "{panel:id}"}` which makes the opportunity id accessible in our action.

```
{
    "type": "ActionSet",
    "actions": [
        {
            "type": "updateDb",
            "title": "Send to DB",
            "data": {
                "id": "{panel:id}"
            }
        }
    ]
}
```

### Action - Javascript
The Action defines the behavior that is performed after the button is clicked. The script below first calls a POST request then redraws the widget to remove the note from the input box.

For our post request to work, we need to add the URL of the API that will accept our POST request along with add the data we are sending in the body. Here, we are sending the opportunity id along with the note the user entered in the input box. 
 
```javascript
url = 'rest-api-url'

const insertOpportunityNote = () => {
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'id': `${payload.data.id}`,
            'note': `${payload.data.note}`
        })
    })
        .then(response => response.json())
        .then(response => console.log(JSON.stringify(response)))
}
insertOpportunityNote()
payload.widget.redraw()
// console.log(payload.data)
```

Most CDW's have APIs that could be leveraged here, such as [Snowflake's SQL API](https://docs.snowflake.com/en/developer-guide/sql-api/about-endpoints). Custom APIs can also be used, which we will explore in the next section. Regardless, CORS must be set up to accept requests from your Sisense IP.

## API & Backend
For this example, AWS Lambda and Amazon API Gateway were used in conjunction to create the REST API functionality that writes to our database. 

### API Gateway
After your Lambda function and API Gateway are connected ([Using Lambda with API Gateway](https://docs.aws.amazon.com/lambda/latest/dg/services-apigateway.html)), double check that CORS is handled correctly in the API. The following headers with correct values must be configured to allow traffic from your Sisense IP.
- Access-Control-Allow-Headers
- Access-Control-Allow-Methods
- Access-Control-Allow-Origin

### Lambda
Our Lambda function uses the psycopg2 library to write to a postgres database. This requires three steps: establish the database connection, execute our insert statement, return a response.

The lambda function accepts the event from the API gateway, extracts the data that was sent from Sisense, then creates our connection. 
```python
# Retrieve the necessary details to connect to the PostgreSQL database
db_host = "your-db-url"
db_port = "5432"
db_name = "mydb"
db_user = "postgres"
db_password = "postgres"

# Retrieve the details of the record to be inserted
db_table = "opportunity_notes"
db_col1_name = "opportunity_id"
db_col1_value = event['id']
db_col2_name = "note_text"
db_col2_value = event['note']

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host=db_host,
    port=db_port,
    dbname=db_name,
    user=db_user,
    password=db_password
)
cur = conn.cursor()
```

Next we build our query, insert the values, and commit the changes. 
```python
# insert query
insert_query = f'''
    INSERT INTO {db_table} ({db_col1_name}, {db_col2_name})\
    VALUES(%s, %s)'''
# Values for the insert query
insert_values = (db_col1_value, db_col2_value)

# Execute the insert query
cur.execute(insert_query, insert_values)

# Commit the changes
conn.commit()
```

Finally we return a response. Note that the headers for CORS have been included here as well. 
```python
return {
    'statusCode': 200,
    'headers': {
        "Content-Type": "application/json",
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Origin': 'https://your-sisense-url.com',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
    },
    'body': 'Record inserted successfully'
}
```

## Final Thoughts
This example of database writeback is very basic. Ideas for enhancing this include:
- Enable BloX to post updates for multiple items
- Add the name or email of the Sisense user to their writeback request for visibility into who created the note
- Enhance security by adding authorization requirements to API Gateway
- Implementing standards in the database to indicate writeback tables
