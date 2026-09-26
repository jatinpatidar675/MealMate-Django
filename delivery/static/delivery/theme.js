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