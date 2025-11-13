document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#individual-view').style.display='none';
  document.querySelector('#compose-view').style.display = 'block';

  // function call
  post_email();
}

function post_email(){
  document.querySelector("#compose-form").onsubmit =() =>{
    const recipientsInput = document.querySelector('#compose-recipients');
    const subjectInput = document.querySelector('#compose-subject');
    const bodyInput = document.querySelector('#compose-body');
    let new_recipients;

    // Extracting the values
    const recipients = recipientsInput.value;
    const subject = subjectInput.value;
    const body = bodyInput.value;

    /* When the user enters multiple recipients separated by spaces replacing them 
    with comma because a comma separated string is required to fetch data from API*/
    if(recipients.includes(' ')){
       new_recipients = recipients.replace(/ /g, ",");
    }
    else{
       new_recipients = recipients;
    }

    fetch('/emails', {
      method: 'POST',
      body: JSON.stringify({
          recipients: new_recipients,
          subject: subject,
          body: body
      })
    })
    .then(response => response.json())
    .then(result => {
      if (result.message){
        // Alerting successful submission
        alert(result.message);

        // Clear input fields
        recipientsInput.value = '';
        subjectInput.value = '';
        bodyInput.value = '';

        load_mailbox('sent');
      }
      if (result.error){
        // Displaying error message
        alert(result.error);
      }
        // Print result in console
        console.log(result);
    })
    .catch(error => {
      console.error("Fetch error:", error);
      // Displaying error message
      alert("An error occurred while sending the email.");
  });
    // Prevents the form from submitting to the server
    return false;
  }
}

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#individual-view').style.display='none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  
  // function call
  fetch_mailbox(mailbox);
}


function fetch_mailbox(mailbox){
  const parentContainer = document.querySelector('#emails-view');
  const url = '/emails/'

  fetch(`${url}${mailbox}`)
  .then(response => response.json())
  .then(emails => {
      emails.forEach(email => {
        let id = email.id;
        let sender = email.sender;
        let subject = email.subject;
        let timestamp = email.timestamp;
        let read = email.read;

        // Creating individual divs
        const element = document.createElement('div');
        if (read){
          element.style.backgroundColor='#ECECEC';
        }
        element.classList.add('indi_mail');
        element.addEventListener('click',() =>{
          open_mail(id,mailbox);
        }) ;

        const sender_info = document.createElement('p');
        sender_info.innerHTML = `From: ${sender}`;
        sender_info.classList.add('left_p');

        const subject_info = document.createElement('p');
        subject_info.innerHTML = `${subject}`;
        subject_info.classList.add('center_p');

        const timestamp_info = document.createElement('p');
        timestamp_info.innerHTML = `${timestamp}`;
        timestamp_info.classList.add('right_p');
        
        // Appending 'p' elements into div(element)
        element.appendChild(sender_info);
        element.appendChild(subject_info);
        element.appendChild(timestamp_info);

        // Appending them inside the parent container
        parentContainer.append(element);
      });
      // Printing in console
      console.log(emails);
  })
  .catch(error => {
    console.error("Fetch error:", error);
    // Displaying error message
    alert("An error occurred while fetching emails ");
});
}


function open_mail(id,mailbox){
  // Shows the individual mail and hides other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#individual-view').style.display='block';
  document.querySelector('#compose-view').style.display = 'none';

  const parentContainer = document.querySelector('#individual-view');
  parentContainer.innerHTML = ''; // Clearing everything
  let url = '/emails/';

  // function call
  toggle_archive(mailbox,url,id);

  fetch(`${url}${id}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  })
  .catch(error => {
    console.error("Fetch error:", error);
  });

  fetch(`${url}${id}`)
  .then(response => response.json())
  .then(email => {
      // Print email
      console.log(email);
      const from = email.sender;
      const to = email.recipients;
      const subject = email.subject;
      const timestamp = email.timestamp;
      const body = email.body;

      const info_element = document.createElement('div');
      info_element.innerHTML = `<span>From: </span>${from}<br><span>To: </span>${to}<br><span>Subject: </span>${subject}<br><span>Timestamp: </span>${timestamp}<br><button class="btn btn-sm btn-outline-primary" id="reply">Reply</button>`;
      info_element.classList.add('info_element');

      const body_element = document.createElement('div');
      body_element.innerHTML = `${body}`;

      // Appending elements inside the parent container
      parentContainer.append(info_element);
      parentContainer.append(body_element);

      // Handling click event on reply button
      document.querySelector('#reply').addEventListener('click',() =>{
        // function call
        compose_email();

        const recipientsInput = document.querySelector('#compose-recipients');
        const subjectInput = document.querySelector('#compose-subject');
        const bodyInput = document.querySelector('#compose-body');
        let sub_val;

        // checking for 'Re:' in the subject line and adding it if not present
        if(subject.includes('Re:')){
          sub_val = subject;
        }
        else{
          sub_val = `Re: ${subject}`;
        }
        recipientsInput.value = from ;
        subjectInput.value = sub_val;
        bodyInput.value = `On ${timestamp} ${from} wrote:\n\n ${body}`;
      })
  })
  .catch(error => {
    console.error("Fetch error:", error);
    // Displaying error message
    alert("An error occurred while fetching requested data");
});
}


function toggle_archive(mailbox,url,id){
  if(mailbox === 'inbox'){
    document.querySelector('#individual-view').innerHTML = '<button class="btn btn-sm btn-outline-primary" id="archive">Archive</button>';
    document.querySelector('#archive').addEventListener('click',() =>{
      fetch(`${url}${id}`, {
        method: 'PUT',
        body: JSON.stringify({
            archived: true
        })
      })
      .then(response =>{
        if(response.ok){
          alert("Successfully Archived!");
        }
        load_mailbox('inbox');
      })
      .catch(error => {
            console.error('Archive error:', error);
        });
    })
  }
  if(mailbox === 'archive'){
    document.querySelector('#individual-view').innerHTML = '<button class="btn btn-sm btn-outline-primary" id="unarchive">Unarchive</button>';
    document.querySelector('#unarchive').addEventListener('click',() =>{
      fetch(`${url}${id}`, {
        method: 'PUT',
        body: JSON.stringify({
            archived: false
        })
      })
      .then(response =>{
        if(response.ok){
          alert("Successfully Unarchived!");
        }
        load_mailbox('inbox');
        
      })
      .catch(error => {
            console.error('Archive error:', error);
        });
    })
  }
}
