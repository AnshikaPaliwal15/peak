document.addEventListener('DOMContentLoaded', () => {
    const calculateBtn = document.getElementById('calculate-btn');
    const resultsSection = document.getElementById('results-section');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');
    const btnSpinner = document.getElementById('btn-spinner');
    const btnText = document.getElementById('btn-text');

    // Input fields
    const genInput = document.getElementById('generated_energy');
    const disInput = document.getElementById('total_discharge');
    const excInput = document.getElementById('total_excess');

    // Result fields (kWh)
    const resGenKwh = document.getElementById('res-gen-kwh');
    const resDisKwh = document.getElementById('res-dis-kwh');
    const resExcKwh = document.getElementById('res-exc-kwh');
    const resLossKwh = document.getElementById('res-loss-kwh');

    // Result fields (MWh)
    const resGenMwh = document.getElementById('res-gen-mwh');
    const resDisMwh = document.getElementById('res-dis-mwh');
    const resExcMwh = document.getElementById('res-exc-mwh');
    const resLossMwh = document.getElementById('res-loss-mwh');

    calculateBtn.addEventListener('click', async () => {
        // Reset state
        errorMessage.style.display = 'none';
        errorText.textContent = '';
        resultsSection.style.display = 'none';

        const genKwh = parseFloat(genInput.value);
        const disKwh = parseFloat(disInput.value);
        const excKwh = parseFloat(excInput.value);

        // 1. Validation: Numbers
        if (isNaN(genKwh) || isNaN(disKwh) || isNaN(excKwh)) {
            showError('Please enter valid numeric values for all metrics.');
            return;
        }

        if (genKwh < 0 || disKwh < 0 || excKwh < 0) {
            showError('Performance metrics cannot be negative values.');
            return;
        }

        // 2. Validation: logical check
        if ((disKwh + excKwh) > genKwh) {
            showError('Constraint error: Discharge + Excess cannot exceed Generated Energy.');
            return;
        }

        try {
            setLoading(true);

            // Determine API URL (helps if running via Live Server on port 5500)
            const apiUrl = window.location.port !== '8000' ? 'http://127.0.0.1:8000/calculate' : '/calculate';

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    generated_energy: genKwh,
                    total_discharge: disKwh,
                    total_excess: excKwh
                })
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({ detail: 'Server processing error.' }));
                throw new Error(errData.detail || 'The request could not be completed at this time.');
            }

            const data = await response.json();
            displayResults(data);

        } catch (err) {
            showError(err.message);
        } finally {
            setLoading(false);
        }
    });

    function setLoading(isLoading) {
        if (isLoading) {
            calculateBtn.disabled = true;
            btnSpinner.style.display = 'block';
            btnText.textContent = 'Persisting...';
        } else {
            calculateBtn.disabled = false;
            btnSpinner.style.display = 'none';
            btnText.textContent = 'Calculate & Persist';
        }
    }

    function showError(msg) {
        errorText.textContent = msg;
        errorMessage.style.display = 'flex';
        resultsSection.style.display = 'none';
        window.scrollTo({ top: errorMessage.offsetTop - 100, behavior: 'smooth' });
    }

    function formatNum(num) {
        return Number(num).toLocaleString(undefined, {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    function displayResults(data) {
        // kWh
        resGenKwh.textContent = formatNum(data.Generated_Energy_kWh);
        resDisKwh.textContent = formatNum(data.Total_Discharge_kWh);
        resExcKwh.textContent = formatNum(data.Total_Excess_kWh);
        resLossKwh.textContent = formatNum(data.Loss_And_Curtailed_kWh);

        // MWh
        resGenMwh.textContent = formatNum(data.Generated_Energy_MWh);
        resDisMwh.textContent = formatNum(data.Total_Discharge_MWh);
        resExcMwh.textContent = formatNum(data.Total_Excess_MWh);
        resLossMwh.textContent = formatNum(data.Loss_And_Curtailed_MWh);

        resultsSection.style.display = 'block';
        window.scrollTo({ top: resultsSection.offsetTop - 40, behavior: 'smooth' });
    }
});
