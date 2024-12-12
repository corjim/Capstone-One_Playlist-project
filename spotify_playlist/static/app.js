document.addEventListener('DOMContentLoaded', () => {

    // Get buttons for tracks and album tracks
    const tracksButton = document.getElementById("toggle-tracks");
    const albumTrackButton = document.getElementById("view-tracks");

    console.log(tracksButton);
    console.log(albumTrackButton);

    // Helper function to toggle display
    function toggleDisplay(elementSelector) {
        const element = document.querySelector(elementSelector);
        if (element) {
            if (element.style.display === "none" || element.style.display === "") {
                element.style.display = "block"; // Show element
            } else {
                element.style.display = "none"; // Hide element
            }
        }
    }

    // Review tracks event listener, shows all tracks when clicked
    if (tracksButton) {
        tracksButton.addEventListener("click", function () {
            toggleDisplay(".show_tracks");
        });
    } else {
        console.warn("tracksButton not found!");
    }

    // View album tracks event listener
    if (albumTrackButton) {
        albumTrackButton.addEventListener("click", function () {
            toggleDisplay(".album-tracks");
        });
    } else {
        console.warn("albumTrackButton not found!");
    }


    // Function to control or play tracks with the play button.
    // NEGLECT>>>>> WORK IN PROGRESS!!
    // const playButtons = document.querySelectorAll('.play-btn');
    // const audioPlayer = new Audio();
    // let currentPlayingButton = null;

    // playButtons.forEach(button => {
    //     button.addEventListener('click', () => {
    //         const audioUrl = button.getAttribute('data-audio-url');

    //         if (audioPlayer.src !== audioUrl || audioPlayer.paused) {
    //             // Stop any currently playing song
    //             audioPlayer.pause();
    //             if (currentPlayingButton) {
    //                 currentPlayingButton.textContent = 'Play';
    //             }

    //             // Play the new song
    //             audioPlayer.src = audioUrl;
    //             audioPlayer.play();
    //             button.textContent = 'Pause';
    //             currentPlayingButton = button;
    //         } else {
    //             // Pause if already playing
    //             audioPlayer.pause();
    //             button.textContent = 'Play';
    //             currentPlayingButton = null;
    //         }
    //     });
    // });

    // Reset button text when playback ends
    // audioPlayer.addEventListener('ended', () => {
    //     if (currentPlayingButton) {
    //         currentPlayingButton.textContent = 'Play';
    //         currentPlayingButton = null;
    //     }

    // });

});



// Timer to auto-hide flash message
setTimeout(() => {
    const flashMessage = document.getElementById("flash-message");
    if (flashMessage) {
        // Fade out effect
        flashMessage.classList.remove("show");
        flashMessage.classList.add("fade");

        // Remove the element after fading out
        setTimeout(() => {
            flashMessage.remove();
        }, 300); // Fade out transition
    } else {
        console.warn("Flash message not found!");
    }
}, 1000); nds



