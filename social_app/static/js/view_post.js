$(document).ready(function () {
    // Edit Comment
    $(".edit-btn").click(function () {
        var commentId = $(this).data('id');
        var content = $("#content-" + commentId);
        var editContent = $("#edit-content-" + commentId);

        content.hide();
        editContent.removeClass("hidden");

        $(this).hide();
        $(".save-btn[data-id='" + commentId + "']").show();
    });

    $(".save-btn").click(function () {
        var commentId = $(this).data('id');
        var updatedContent = $("#edit-content-" + commentId).val();

        $.ajax({
            url: "{% url 'edit_comment' %}",
            method: 'POST',
            data: {
                'comment_id': commentId,
                'content': updatedContent,
                'csrfmiddlewaretoken': '{{ csrf_token }}',
            },
            success: function (response) {
                if (response.success) {
                    $("#content-" + commentId).text(updatedContent).show();
                    $("#edit-content-" + commentId).addClass("hidden");
                    $(".save-btn[data-id='" + commentId + "']").hide();
                    $(".edit-btn[data-id='" + commentId + "']").show();
                } else {
                    alert("Failed to update comment. Error: " + response.error);
                }
            },
            error: function () {
                alert("An error occurred. Please try again.");
            }
        });
    });
    $(".delete-btn").click(function () {
        var commentId = $(this).data('id');
          $.ajax({
              url: "{% url 'delete_comment' %}",
              method: 'POST',
              data: {
                  'comment_id': commentId,
                  'csrfmiddlewaretoken': '{{ csrf_token }}',
              },
              success: function (response) {
                  if (response.success) {
                      $("#comment-" + commentId).remove();
                      var currentCommentCount = parseInt($("#post-comments-count").text());
                      $("#post-comments-count").text(currentCommentCount - 1);
                  } else {
                      alert("Failed to delete comment. Error: " + response.error);
                  }
              },
              error: function () {
                  alert("An error occurred. Please try again.");
              }
          });
    });
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
    // Edit Post
    $(".edit-post").click(function () {
        var postId = $(this).data('post-id');
        var content = $("#post-content-" + postId);
        var editContent = $("#edit-post-content-" + postId);

        content.hide();
        editContent.removeClass("hidden");

        $(this).addClass("hidden");
        $(".save-post-btn[data-post-id='" + postId + "']").removeClass("hidden");
    });

    $(".save-post-btn").click(function () {
        var postId = $(this).data('post-id');
        var updatedContent = $("#edit-post-content-" + postId).val();

        $.ajax({
            url: "{% url 'edit_post' %}",
            method: 'POST',
            data: {
                'post_id': postId,
                'content': updatedContent,
                'csrfmiddlewaretoken': '{{ csrf_token }}',
            },
            success: function (response) {
                if (response.status === 'success') {
                    // Update the content in the UI
                    $("#post-content-" + postId).text(updatedContent).show();
                    $("#edit-post-content-" + postId).addClass("hidden");

                    // Toggle the visibility of buttons
                    $(".save-post-btn[data-post-id='" + postId + "']").addClass("hidden");
                    $(".edit-post[data-post-id='" + postId + "']").removeClass("hidden");
                } else {
                    alert("Failed to update post. Error: " + response.message);
                }
            },
            error: function () {
                alert("An error occurred. Please try again.");
            }
        });
    });
});