// Main JS for KeyPilot

document.addEventListener('DOMContentLoaded', () => {
    // Modal handling
    window.openModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            document.body.style.overflow = 'hidden'; // Prevent background scroll
        }
    };

    window.closeModal = function(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
            document.body.style.overflow = '';
        }
    };

    // Close modal on click outside content
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                const modal = overlay.closest('.modal-container');
                if (modal) {
                    closeModal(modal.id);
                }
            }
        });
    });

    // Copy to clipboard
    window.copyToClipboard = function(elementId) {
        const text = document.getElementById(elementId).innerText;
        navigator.clipboard.writeText(text).then(() => {
            const btn = document.getElementById('copy-btn-' + elementId);
            const originalText = btn.innerText;
            btn.innerText = 'Copied!';
            setTimeout(() => {
                btn.innerText = originalText;
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy: ', err);
        });
    };
});
