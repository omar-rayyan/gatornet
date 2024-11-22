$(document).ready(function () {
    $(".like-btn").click(function () {
        var postId = $(this).data('post-id');
        var likeButton = $(this);

        // Prevent multiple clicks
        if (likeButton.hasClass('loading')) return;
        likeButton.addClass('loading');

        // Send AJAX request
        $.ajax({
            url: "{% url 'like_post' %}",
            method: 'POST',
            data: {
                'post_id': postId,
                'csrfmiddlewaretoken': '{{ csrf_token }}',
            },
            success: function (response) {
                if (response.success) {
                    // Update the like count and button state
                    if (response.liked) {
                        likeButton.addClass('text-green-700');
                    } else {
                        likeButton.removeClass('text-green-700');
                    }

                    // Update like count
                    var currentLikeCount = parseInt($(".like-count").text());
                    $(".like-count").text(response.like_count + " likes");

                } else {
                    alert("Failed to like/unlike the post.");
                }
            },
            error: function () {
                alert("An error occurred. Please try again.");
            },
            complete: function () {
                likeButton.removeClass('loading');
            }
        });
    });
    $(".delete-post-btn").click(function () {
        var postId = $(this).data('post-id');
        var deleteButton = $(this);

        if (deleteButton.hasClass('loading')) return;
        deleteButton.addClass('loading');

        $.ajax({
            url: "{% url 'delete_post' %}",
            method: 'POST',
            data: {
                'post_id': postId,
                'csrfmiddlewaretoken': '{{ csrf_token }}',
            },
            success: function (response) {
                if (response.success) {
                    deleteButton.closest('.post-container').remove();
                } else {
                    alert(response.error || "Failed to delete the post.");
                }
            },
            error: function () {
                alert("An error occurred. Please try again.");
            },
            complete: function () {
                deleteButton.removeClass('loading');
            }
        });
    });
    $(".remove-friend-btn").click(function () {
        var friendId = $(this).data('friend-id');
        var button = $(this);

        // Disable the button to prevent multiple clicks
        button.prop('disabled', true);

        $.ajax({
            url: "{% url 'remove_friend' %}",
            method: "POST",
            data: {
                'friend_id': friendId,
                'csrfmiddlewaretoken': '{{ csrf_token }}',
            },
            success: function (response) {
                if (response.success) {
                    // Remove the friend from the UI
                    button.closest('.friend-container').remove();
                } else {
                    alert(response.error || "An error occurred.");
                }
            },
            error: function () {
                alert("Failed to remove friend. Please try again.");
            },
            complete: function () {
                // Re-enable the button
                button.prop('disabled', false);
            }
        });
    });
    $(".add-friend-btn").click(function () {
        var friendId = $(this).data('friend-id');
        var button = $(this);
    
        // Disable the button to prevent multiple clicks
        button.prop('disabled', true);
    
        $.ajax({
            url: "{% url 'add_friend' %}",
            method: "POST",
            data: {
                'friend_id': friendId,
                'csrfmiddlewaretoken': '{{ csrf_token }}',
            },
            success: function (response) {
                if (response.success) {
                    // Optionally, update the button or UI
                    button.text("Friend Added").addClass("text-green-500").prop('disabled', true);
                } else {
                    alert(response.error || "An error occurred.");
                }
            },
            error: function () {
                alert("Failed to add friend. Please try again.");
            },
            complete: function () {
                // Re-enable the button if needed
                button.prop('disabled', false);
            }
        });
    });    
});