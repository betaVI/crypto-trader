import dashboard from '../pages/dashboard.js';
import diagnostics from '../pages/diagnostics.js';
import settings from '../pages/settings.js';

export default {
    "/": dashboard,
    '/diagnostics': diagnostics,
    '/settings': settings
}