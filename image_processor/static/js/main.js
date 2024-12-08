document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('imageForm');
    const processButton = document.getElementById('processButton');
    const downloadButton = document.getElementById('downloadButton');
    const resultImage = document.getElementById('resultImage');
    const errorMessage = document.getElementById('errorMessage');
    const loadingIndicator = document.getElementById('loading');
    const autoOptimizeCheckbox = document.getElementById('auto-optimize');
    const enhancementOptions = document.querySelectorAll('.enhancement-option');

    if (form && processButton) {
        console.log("Image Processing Page Loaded");

        document.querySelectorAll('input[type="range"]').forEach(slider => {
            // Update displayed value when slider is adjusted
            slider.addEventListener('input', (event) => {
                const valueSpan = document.getElementById(slider.id + "Value");
                valueSpan.textContent = event.target.value;
            });
        });

        processButton.addEventListener('click', async () => {
            // Reset error message, result image visibility
            // Reset download button visibility
            errorMessage.textContent = '';
            resultImage.style.display = 'none';
            downloadButton.style.display = 'none';
            loadingIndicator.style.display = 'block';

            const formData = new FormData(form);

            // Gather enhancement options
            const enhancements = [];
            document.querySelectorAll('input[name="enhancements"]:checked').forEach(input => {
                enhancements.push(input.value);
            });
            formData.append('enhancements', JSON.stringify(enhancements));

            try {
                // Send image processing request to server
                const response = await fetch('/convert', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCSRFToken(),
                    },
                });

                if (response.ok) {
                    // Display processed image
                    const blob = await response.blob();
                    const imageUrl = URL.createObjectURL(blob);
                    resultImage.src = imageUrl;
                    resultImage.style.display = 'block';
                    resultImage.dataset.downloadUrl = imageUrl;
                    downloadButton.style.display = 'block';
                } else {
                    // Display error message
                    const errorData = await response.json();
                    errorMessage.textContent = errorData.error || 'An unknown error occurred.';
                }
            } catch (error) {
                errorMessage.textContent = 'Failed to connect to the server.';
            } finally {
                // Hide loading indicator
                loadingIndicator.style.display = 'none';
            }
        });

        downloadButton.addEventListener('click', () => {
            // Trigger download of processed image
            const downloadUrl = resultImage.dataset.downloadUrl;

            if (downloadUrl) {
                const a = document.createElement('a');
                a.href = downloadUrl;

                const filename = 'processed_image.jpg';
                a.download = filename;

                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(downloadUrl);
            } else {
                errorMessage.textContent = 'No image available to download.';
            }
        });

        autoOptimizeCheckbox.addEventListener('change', (event) => {
            // Enable or disable other enhancement options
            // based on auto-optimize checkbox
            if (event.target.checked) {
                enhancementOptions.forEach(option => {
                    option.disabled = true;
                });
            } else {
                enhancementOptions.forEach(option => {
                    option.disabled = false;
                });
            }
        });

        enhancementOptions.forEach(option => {
            // Enable or disable auto-optimize options
            // based on other enhancement checkbox
            option.addEventListener('change', () => {
                const anyChecked = Array.from(enhancementOptions).some(opt => opt.checked);
                autoOptimizeCheckbox.disabled = anyChecked;
            });
        });
    }

    const styleForm = document.getElementById('styleForm');
    const styleProcessButton = document.getElementById('styleProcessButton');
    const styleLoading = document.getElementById('styleLoading');
    const styleErrorMessage = document.getElementById('styleErrorMessage');
    const styleResultImage = document.getElementById('styleResultImage');
    const styleDownloadButton = document.getElementById('styleDownloadButton');

    if (styleForm && styleProcessButton) {
        console.log("Style Transfer Page Loaded");

        styleProcessButton.addEventListener('click', async () => {
            // Reset error message and result image visibility
            styleErrorMessage.textContent = '';
            styleResultImage.style.display = 'none';
            styleLoading.style.display = 'block';

            const formData = new FormData(styleForm);

            try {
                // Send style transfer request to server
                const response = await fetch('/process_style_transfer', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': getCSRFToken(),
                    },
                });

                if (response.ok) {
                    // Display styled image
                    const data = await response.json();
                    styleResultImage.src = data.result_image;
                    styleResultImage.style.display = 'block';
                    styleDownloadButton.style.display = 'block';

                    styleDownloadButton.onclick = () => {
                        // Enable download of styled image
                        const a = document.createElement('a');
                        a.href = data.result_image;
                        a.download = 'styled_image.jpg';
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                    };
                } else {
                    // Display error message
                    const errorData = await response.json();
                    styleErrorMessage.textContent = errorData.error || 'An unknown error occurred.';
                }
            } catch (error) {
                styleErrorMessage.textContent = 'Failed to connect to the server.';
            } finally {
                styleLoading.style.display = 'none';
            }
        });
    }

    function getCSRFToken() {
        // Retrieve CSRF token from the form
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfInput ? csrfInput.value : '';
    }
});
