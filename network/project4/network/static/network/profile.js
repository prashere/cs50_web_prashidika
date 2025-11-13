document.addEventListener('DOMContentLoaded', () => {
    const follow = document.querySelector('#follow');

    if (follow != null) {
        const creator_id = follow.getAttribute('data-user-id');// getting the creator_id
        const is_following = follow.getAttribute('data-following');// getting the boolean value that denotes if the current user is following the creator or not

        if (is_following === 'True') {
            follow.innerHTML = 'Following';
        }
        else {
            follow.innerHTML = 'Follow';
        }

        // Handling click on the buton
        follow.addEventListener('click', () => {
            const currentContent = follow.innerHTML;// Getting the text of the button

            if (currentContent.includes('Following')){
              // if user clicks the button while the text is 'Following' then 
              // changing the text to 'Follow' and unfollowing the creator
                follow.innerHTML = 'Follow';

                fetch(`/unfollow/${creator_id}`, {
                    method: 'POST'
                })
                    .then(response => response.json())
                    .then(data => {
                        console.log(data.message);
                        window.location.reload();
                    })
                    .catch(error => {
                        console.log(error);
                    })
            }
            else {
              // if user clicks the button while the text is 'Follow' then 
              // changing the text to 'Following' and following the creator
                follow.innerHTML = 'Following';
                fetch(`/follow/${creator_id}`, {
                    method: 'POST'
                })
                    .then(response => response.json())
                    .then(data => {
                        console.log(data.message);
                        window.location.reload();
                    })
                    .catch(error => {
                        console.log(error);
                    })
            }
        })
    }//end of outer if block

    

    const allEditBtns = document.querySelectorAll('.edit') // getting all the buttons with class 'edit' 
    allEditBtns.forEach(btn => { // looping ver individual buttons
        btn.addEventListener('click', () => {
            const postId = btn.getAttribute('data-post-id'); // getting the value of postId
            // Selecting corresponding elements for  this post 
            const saveBtn = document.querySelector(`#save-${postId}`);
            const contentContainer = document.querySelector(`#content-${postId}`);
            const txtArea = document.querySelector(`#txtarea-${postId}`);

            const content = contentContainer.textContent;

            btn.style.display = 'none'; // hiding the element
            contentContainer.style.display = 'none'; // hiding the element
            saveBtn.style.display = 'inline-block';
            txtArea.style.display = 'block';

            txtArea.innerHTML = content; //Populating the textArea with content of the post

            saveBtn.addEventListener('click', () => {
                new_content = txtArea.value;

                fetch(`/edit/${postId}`,
                    {
                        method: 'POST',
                        body: JSON.stringify({ content: new_content })
                    })
                    .then(response => response.json())
                    .then(data => {
                        contentContainer.textContent = new_content;

                        btn.style.display = 'inline-block';
                        contentContainer.style.display = 'block';
                        saveBtn.style.display = 'none'; // hiding the element
                        txtArea.style.display = 'none'; // hiding the element
                    })
                    .catch(error => {
                        console.log(error);
                    })
            })
        })
    });


    const icons =document.querySelectorAll('#heart');// getting all the icons with id 'heart'
    icons.forEach(icon =>{ //looping over inividual icons
      const postId = icon.getAttribute('data-post-id');
      const likeContainer = document.querySelector(`#like-count-${postId}`);
      const userId  =icon.getAttribute('data-user-id');

      // fetching the information of whether current user has liked the post or not and number of likes of the post
      fetch(`/loadlikes/${postId}/${userId}`,{method:'POST'})
      .then(response => response.json())
      .then(data => {
        console.log(data)
        // setting 'data-liked' attribute of icon to what is returned from the url
        icon.setAttribute('data-liked', data.is_liked);

        // Displaying appropriate icon
        if(data.is_liked === true){
          icon.classList.add('fa-solid');
        }
        else{
          icon.classList.add('fa-regular');
        }
        // setting the like count
        likeContainer.innerHTML = data.like_count;

      })
      .catch(error => {
        console.log('Like update error',error)
      })
      
      // Handling click events on the like button
      icon.addEventListener('click' , () => {
        const postId = icon.getAttribute('data-post-id');
        const userId  =icon.getAttribute('data-user-id');
        const isLiked=icon.getAttribute('data-liked') === 'true';
        const container = document.querySelector(`#like-count-${postId}`);

        icon.classList.toggle('fa-solid');
        icon.setAttribute('data-liked',!isLiked);

        const url = isLiked?`/unlike/${postId}/${userId}`: `/like/${postId}/${userId}`

        fetch(url,{method:'POST'})
        .then(response => response.json())
        .then(data => {
          if(data.message){
            console.log(data.message);
            // updating the like count after click
            container.innerHTML = data.like_count;
          }
          else if (data.error){
            console.log(data.error);
          }
        })
        .catch(error =>{
          console.log('Like/Unlike error', error)
        })
      });
    }); 

});// end of 'DOMContentLoaded' block
