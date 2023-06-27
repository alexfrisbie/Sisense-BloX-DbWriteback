import psycopg2


def lambda_handler(event, context):
    # Retrieve the necessary details to connect to the PostgreSQL database
    db_host = ""
    db_port = "5432"
    db_name = "mydb"
    db_user = "postgres"
    db_password = "postgres"
    
    # Retrieve the details of the record to be inserted
    db_table = "opportunity_notes"
    try:
        db_col1_name = "opportunity_id"
        db_col1_value = event['id']
        db_col2_name = "note_text"
        db_col2_value = event['note']
    except Exception as e:
        # Return an error message
        return {
            'statusCode': 500,
            'headers': {
                "Content-Type": "application/json",
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': 'https://your-sisense-ip.com',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': f'An error occurred: {str(e)}.\n event param is {event}'
        }

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        dbname=db_name,
        user=db_user,
        password=db_password
    )
    cur = conn.cursor()

    # Perform the record insert
    try:
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

        # Return a success message
        return {
            'statusCode': 200,
            'headers': {
                "Content-Type": "application/json",
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': 'https://your-sisense-ip.com',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': 'Record inserted successfully'
        }
    except Exception as e:
        # Rollback the transaction in case of an error
        conn.rollback()

        # Return an error message
        return {
            'statusCode': 500,
            'headers': {
                "Content-Type": "application/json",
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Origin': 'https://your-sisense-ip.com',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': f'Error updating record: {str(e)}'
        }
    finally:
        # Close the database connection
        cur.close()
        conn.close()
