// PASTE THIS CODE INTO templates/feed.html
// Replace the addComment function (around line 875-925)

function addComment(event, postId) {
    event.preventDefault();

    const input = document.getElementById(`comment-input-${postId}`);
    const content = input.value.trim();
    const postBtn = document.getElementById(`post-btn-${postId}`);

    if (!content) return;

    // Disable button during submission
    postBtn.disabled = true;
    postBtn.innerHTML = '\u003cspan class="spinner-border spinner-border-sm" role="status"\u003e\u003c/span\u003e';

    fetch(`/comment/${postId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: content })
    })
        .then(response => {
            // ✨ NEW: Proper error handling
            if (!response.ok) {
                return response.json().then(err => Promise.reject(err));
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                const commentsList = document.getElementById(`comments-${postId}`);
                const newComment = document.createElement('div');
                newComment.className = 'comment-item';
                newComment.innerHTML = `
                \u003cspan class="comment-username"\u003e${data.comment.username}\u003c/span\u003e
                \u003cspan class="comment-text"\u003e${data.comment.content}\u003c/span\u003e
                ${data.comment.is_flagged ? '\u003ci class="fas fa-exclamation-triangle text-warning ms-1" title="Flagged content"\u003e\u003c/i\u003e' : ''}
            `;
                commentsList.appendChild(newComment);
                input.value = '';

                // Silent crime detection handling
                if (data.comment.is_flagged) {
                    console.log('Content flagged for review');
                    setTimeout(() => {
                        const modal = new bootstrap.Modal(document.getElementById('silentCrimeAlert'));
                        modal.show();
                        setTimeout(() => modal.hide(), 2000);
                    }, 1000);
                }
            }
        })
        .catch(error => {
            // ✨ NEW: Show warning modal for vulgar content
            if (error.blocked && error.reason === 'inappropriate_content') {
                if (typeof showVulgarContentWarning === 'function') {
                    showVulgarContentWarning(error.error);
                } else {
                    alert(error.error);
                }
                input.value = ''; // Clear the inappropriate comment
            } else if (error.error) {
                console.error('Error adding comment:', error);
                alert(error.error);
            } else {
                console.error('Error adding comment:', error);
                alert('Failed to add comment. Please try again.');
            }
        })
        .finally(() => {
            postBtn.innerHTML = 'Post';
            postBtn.disabled = true; // Keep disabled since input is now empty
        });
}
