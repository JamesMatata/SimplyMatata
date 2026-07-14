(function () {
    'use strict';

    const FORMAT_CATEGORIES = new Set(['film', 'comic', 'advertising']);

    const DETAIL_FIELDS = [
        'overview',
        'additional',
        'tools',
        'meta_year',
        'meta_role',
        'meta_client',
    ];

    const VISIBLE_DETAIL_FIELDS = {
        software: ['overview', 'additional', 'tools', 'meta_year', 'meta_role'],
        lab: ['overview', 'additional', 'meta_year', 'meta_role'],
        film: ['overview', 'additional', 'meta_year', 'meta_role', 'meta_client'],
        comic: ['overview', 'additional', 'meta_year', 'meta_role'],
        advertising: ['overview', 'additional', 'meta_year', 'meta_role', 'meta_client'],
    };

    const ABOUT_DESCRIPTIONS = {
        software: (
            'Optional. Overview and notes appear in About; tools show in a dedicated stack section. '
            'Year and role appear in the project header when filled in.'
        ),
        lab: (
            'Optional. Notes and credits for the project page header and About section.'
        ),
        film: (
            'Optional. Overview and notes appear in About. Year, role, and client appear in the project header.'
        ),
        comic: (
            'Optional. Story notes in About; year and role appear in the project header. '
            'Comic pages are added after you save the project.'
        ),
        advertising: (
            'Optional. Campaign notes in About. Year, role, and client appear in the project header.'
        ),
    };

    const FORMAT_DESCRIPTIONS = {
        film: (
            'Single = one film with video on this page. '
            'Series = multiple episodes — save first, then add entries below.'
        ),
        comic: (
            'Single = one comic — save first, then add pages below (page 1 is usually the cover). '
            'Series = multiple issues managed as episodes below.'
        ),
        advertising: (
            'Single = one ad with video on this page. '
            'Series = multiple cuts — save first, then add entries below.'
        ),
    };

    function getFieldRow(fieldName) {
        return document.querySelector('.form-row.field-' + fieldName);
    }

    function setRowVisible(fieldName, visible) {
        const row = getFieldRow(fieldName);
        if (row) {
            row.style.display = visible ? '' : 'none';
        }
    }

    function findFieldsetContaining(fieldName) {
        const row = getFieldRow(fieldName);
        return row ? row.closest('fieldset.module') : null;
    }

    function updateAboutSection(category) {
        const visible = new Set(VISIBLE_DETAIL_FIELDS[category] || VISIBLE_DETAIL_FIELDS.software);

        DETAIL_FIELDS.forEach(function (fieldName) {
            setRowVisible(fieldName, visible.has(fieldName));
        });

        const fieldset = findFieldsetContaining('overview');
        if (!fieldset) {
            return;
        }

        const description = fieldset.querySelector('.description');
        if (description) {
            description.textContent = ABOUT_DESCRIPTIONS[category] || ABOUT_DESCRIPTIONS.software;
        }
    }

    function updateFormatSection(category) {
        const showFormat = FORMAT_CATEGORIES.has(category);

        setRowVisible('format', showFormat);
        setRowVisible('delivery_formats', category === 'advertising');

        const fieldset = findFieldsetContaining('format') || findFieldsetContaining('delivery_formats');
        if (fieldset) {
            fieldset.style.display = showFormat ? '' : 'none';

            const description = fieldset.querySelector('.description');
            if (description && FORMAT_DESCRIPTIONS[category]) {
                description.textContent = FORMAT_DESCRIPTIONS[category];
            }
        }
    }

    function init() {
        const categorySelect = document.getElementById('id_category');
        if (!categorySelect) {
            return;
        }

        function applyCategoryRules() {
            const category = categorySelect.value || 'software';
            updateAboutSection(category);
            updateFormatSection(category);
        }

        categorySelect.addEventListener('change', applyCategoryRules);
        applyCategoryRules();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
