/**
 * Custom tooltip transform functions for date sliders.
 * These functions convert slider percentage values to date strings.
 */

// Global storage for date ranges
window.sliderDateRanges = {
    dataRange: { min: null, max: null },
    refPeriod: { min: null, max: null }
};

/**
 * Transform function for data range slider tooltip.
 * Converts percentage (0-100) to date string.
 */
window.dccFunctions = window.dccFunctions || {};

window.dccFunctions.dataRangeTooltip = function(value) {
    const dateRange = window.sliderDateRanges.dataRange;
    if (!dateRange.min || !dateRange.max) {
        return value.toFixed(0) + '%';
    }
    
    try {
        const minDate = new Date(dateRange.min);
        const maxDate = new Date(dateRange.max);
        const totalMs = maxDate.getTime() - minDate.getTime();
        const targetMs = minDate.getTime() + (totalMs * value / 100);
        const targetDate = new Date(targetMs);
        
        // Format as YYYY-MM-DD
        return targetDate.toISOString().split('T')[0];
    } catch (e) {
        return value.toFixed(0) + '%';
    }
};

window.dccFunctions.refPeriodTooltip = function(value) {
    // Uses same date range as data range slider
    return window.dccFunctions.dataRangeTooltip(value);
};
