document.addEventListener('DOMContentLoaded', function() {
    console.log('Wonliy POS Loaded');
    
    // Barcode Scanner Helper
    // Most USB scanners act as keyboards. 
    // This script ensures that if a user scans a barcode while not focused on an input,
    // we can try to intelligently handle it or focus the main search/input box.
    
    const barcodeInput = document.querySelector('input[name="barcode"]');
    const searchInput = document.querySelector('input[name="search_barcode"]');

    if (barcodeInput) {
        barcodeInput.focus();
    } else if (searchInput) {
        searchInput.focus();
    }

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
});
