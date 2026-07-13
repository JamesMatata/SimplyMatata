/**
 * Trap keyboard focus inside a modal container.
 * Returns a release function that restores the previous focus.
 */
function createFocusTrap(container) {
    if (!container) {
        return function () {};
    }

    const focusableSelector = [
        'button:not([disabled])',
        '[href]',
        'input:not([disabled])',
        'select:not([disabled])',
        'textarea:not([disabled])',
        '[tabindex]:not([tabindex="-1"])',
    ].join(', ');

    const previousFocus = document.activeElement;

    function getFocusable() {
        return Array.from(container.querySelectorAll(focusableSelector))
            .filter(function (element) {
                return element.offsetParent !== null || element === document.activeElement;
            });
    }

    function onKeyDown(event) {
        if (event.key !== 'Tab') {
            return;
        }

        const focusable = getFocusable();
        if (!focusable.length) {
            return;
        }

        const first = focusable[0];
        const last = focusable[focusable.length - 1];

        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus();
        }
    }

    container.addEventListener('keydown', onKeyDown);

    const initialFocus = getFocusable()[0];
    if (initialFocus) {
        initialFocus.focus();
    }

    return function releaseFocusTrap() {
        container.removeEventListener('keydown', onKeyDown);
        if (previousFocus && typeof previousFocus.focus === 'function') {
            previousFocus.focus();
        }
    };
}
