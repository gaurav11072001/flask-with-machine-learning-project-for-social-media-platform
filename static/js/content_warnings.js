// Content Warning System for Vulgar and NSFW Content

function showVulgarContentWarning(message) {
    const modalHtml = `
        <div class="modal fade" id="vulgarContentWarningModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-warning" style="border-width: 2px;">
                    <div class="modal-header" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white;">
                        <h5 class="modal-title">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Inappropriate Content Detected
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p class="mb-2"><strong>⚠️ Your content was blocked.</strong></p>
                        <p class="mb-3">${message || 'Your comment contains inappropriate content and cannot be posted. Please keep comments respectful and appropriate.'}</p>
                        <div class="alert alert-info mb-0">
                            <i class="fas fa-info-circle me-2"></i>
                            Please review our community guidelines and keep your content respectful.
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" data-bs-dismiss="modal">Understood</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    const existingModal = document.getElementById('vulgarContentWarningModal');
    if (existingModal) existingModal.remove();

    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('vulgarContentWarningModal'));
    modal.show();

    // Auto-remove modal from DOM after it's hidden
    document.getElementById('vulgarContentWarningModal').addEventListener('hidden.bs.modal', function () {
        this.remove();
    });
}

function showNSFWContentWarning() {
    const modalHtml = `
        <div class="modal fade" id="nsfwContentWarningModal" tabindex="-1">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content border-danger" style="border-width: 2px;">
                    <div class="modal-header" style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white;">
                        <h5 class="modal-title">
                            <i class="fas fa-eye-slash me-2"></i>
                            NSFW Content Detected
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p class="mb-2"><strong>🔞 Your post contains sensitive content.</strong></p>
                        <p class="mb-3">Your post has been flagged as NSFW (Not Safe For Work) and will be hidden from users who have NSFW content filtering enabled.</p>
                        <div class="alert alert-warning mb-0">
                            <i class="fas fa-shield-alt me-2"></i>
                            <strong>Note:</strong> Repeated violations of our content policy may result in account restrictions.
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-primary" data-bs-dismiss="modal">I Understand</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Remove existing modal if any
    const existingModal = document.getElementById('nsfwContentWarningModal');
    if (existingModal) existingModal.remove();

    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('nsfwContentWarningModal'));
    modal.show();

    // Auto-remove modal from DOM after it's hidden
    document.getElementById('nsfwContentWarningModal').addEventListener('hidden.bs.modal', function () {
        this.remove();
    });
}

// Export functions for global use
window.showVulgarContentWarning = showVulgarContentWarning;
window.showNSFWContentWarning = showNSFWContentWarning;

// Check for existing flash messages that should trigger warnings
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (alert.textContent.includes('Your post has been shared but flagged for review due to potentially harmful content')) {
            showNSFWContentWarning();
        }
    });
});
