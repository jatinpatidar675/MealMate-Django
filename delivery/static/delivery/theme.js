(() => {
    const storageKey = 'mealmate-theme';
    const savedTheme = localStorage.getItem(storageKey);
    const preferredTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';

    document.documentElement.dataset.theme = savedTheme || preferredTheme;

    const button = document.createElement('button');
    button.className = 'theme-toggle';
    button.type = 'button';
    button.setAttribute('aria-label', 'Switch color theme');
    button.setAttribute('title', 'Switch color theme');
    button.innerHTML = '<span class="theme-toggle__icon" aria-hidden="true"></span><span class="theme-toggle__label">Theme</span>';

    const updateButton = () => {
        const isDark = document.documentElement.dataset.theme === 'dark';
        button.setAttribute('aria-pressed', String(isDark));
        button.setAttribute('aria-label', `Switch to ${isDark ? 'light' : 'dark'} mode`);
        button.setAttribute('title', `Switch to ${isDark ? 'light' : 'dark'} mode`);
    };

    button.addEventListener('click', () => {
        const nextTheme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
        document.documentElement.dataset.theme = nextTheme;
        localStorage.setItem(storageKey, nextTheme);
        updateButton();
    });

    updateButton();
    document.addEventListener('DOMContentLoaded', () => {
        document.body.append(button);

        document.querySelectorAll('.password-toggle').forEach((toggle) => {
            const password = document.getElementById(toggle.dataset.target);
            if (!password) return;

            toggle.addEventListener('click', () => {
                const isVisible = password.type === 'text';
                password.type = isVisible ? 'password' : 'text';
                toggle.setAttribute('aria-pressed', String(!isVisible));
                toggle.setAttribute('aria-label', `${isVisible ? 'Show' : 'Hide'} password`);
            });
        });

        document.querySelectorAll('.location-action').forEach((locationButton) => {
            const address = document.getElementById(locationButton.dataset.locationTarget);
            const status = document.querySelector(`[data-location-status="${locationButton.dataset.locationTarget}"]`);
            if (!address || !status || !navigator.geolocation) {
                locationButton.hidden = true;
                return;
            }

            locationButton.addEventListener('click', () => {
                locationButton.disabled = true;
                status.textContent = 'Finding your location...';

                navigator.geolocation.getCurrentPosition(async ({ coords }) => {
                    try {
                        const query = new URLSearchParams({
                            format: 'jsonv2',
                            lat: String(coords.latitude),
                            lon: String(coords.longitude),
                            addressdetails: '1',
                            zoom: '18',
                            'accept-language': 'en',
                        });
                        const response = await fetch(`https://nominatim.openstreetmap.org/reverse?${query}`);
                        if (!response.ok) throw new Error('Location lookup failed');
                        const result = await response.json();
                        const addressParts = result.address || {};
                        const parts = [
                            [addressParts.house_number, addressParts.road].filter(Boolean).join(' '),
                            addressParts.neighbourhood,
                            addressParts.suburb,
                            addressParts.city_district,
                            addressParts.city || addressParts.town || addressParts.village || addressParts.municipality,
                            addressParts.state_district,
                            addressParts.state,
                            addressParts.postcode,
                            addressParts.country,
                        ].filter((part, index, values) => part && values.indexOf(part) === index);
                        if (!parts.length) throw new Error('No address found');
                        address.value = parts.join(', ').slice(0, Number(address.maxLength) || 250);
                        status.textContent = 'Location added. Check the address before saving.';
                    } catch (error) {
                        status.textContent = 'We could not find the address. Please enter it manually.';
                    } finally {
                        locationButton.disabled = false;
                    }
                }, () => {
                    status.textContent = 'Location permission was unavailable. Please enter the address manually.';
                    locationButton.disabled = false;
                }, { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 });
            });
        });

        document.querySelectorAll('.toast').forEach((toast) => {
            const dismiss = () => {
                toast.classList.add('toast--leaving');
                window.setTimeout(() => toast.remove(), 180);
            };

            toast.querySelector('.toast__dismiss').addEventListener('click', dismiss);
            window.setTimeout(dismiss, 4500);
        });
    }, { once: true });
})();