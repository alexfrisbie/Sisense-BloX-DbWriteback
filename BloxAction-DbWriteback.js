/*
This code should be inserted into a new custom action. 
The name of the custom action must match the 'type' value of the action defined in the editor.
In this example, the name should be 'updateDb'
*/
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
