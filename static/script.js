document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('uploadForm');
    const evaluateBtn = document.getElementById('evaluateBtn');
    const btnText = document.getElementById('btnText');
    const loadingIcon = document.getElementById('loadingIcon');
    const resultsSection = document.getElementById('resultsSection');
    const resultsBody = document.getElementById('resultsBody');

    // File Input Highlighting
    const jdInput = document.getElementById('jd');
    const jdFileName = document.getElementById('jdFileName');
    const resumesInput = document.getElementById('resumes');
    const resumesFileName = document.getElementById('resumesFileName');

    jdInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            jdFileName.textContent = e.target.files[0].name;
            jdFileName.classList.add('text-blue-400');
        } else {
            jdFileName.textContent = "PDF, DOCX, TXT";
            jdFileName.classList.remove('text-blue-400');
        }
    });

    resumesInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            resumesFileName.textContent = `${e.target.files.length} files selected`;
            resumesFileName.classList.add('text-green-400');
        } else {
            resumesFileName.textContent = "Upload multiple files";
            resumesFileName.classList.remove('text-green-400');
        }
    });

    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Show loading
        evaluateBtn.disabled = true;
        btnText.textContent = 'Analyzing...';
        loadingIcon.classList.remove('hidden');
        resultsSection.classList.add('hidden');
        resultsBody.innerHTML = '';

        const formData = new FormData(uploadForm);

        try {
            const response = await fetch('/evaluate', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Evaluation failed');
            }

            const results = await response.json();
            displayResults(results);

        } catch (error) {
            alert(`Error: ${error.message}`);
        } finally {
            // Reset button
            evaluateBtn.disabled = false;
            btnText.textContent = 'Evaluate Capabilities';
            loadingIcon.classList.add('hidden');
        }
    });

    function displayResults(results) {
        resultsSection.classList.remove('hidden');

        results.forEach((result, index) => {
            const row = document.createElement('tr');
            row.className = 'result-row border-b border-gray-700 last:border-0';

            // Score handling
            const score = result.score;
            let statusBadge = '';

            // Threshold Logic (Boosted Scores)
            if (score >= 70) {
                statusBadge = '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-900 text-green-200">Excellent Match</span>';
            } else if (score >= 30) {
                statusBadge = '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-900 text-yellow-200">Potential</span>';
            } else {
                statusBadge = '<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-900 text-red-200">Low Match</span>';
            }

            row.innerHTML = `
                <td class="px-6 py-4 whitespace-nowrap text-gray-400">#${result.rank}</td>
                <td class="px-6 py-4 font-medium text-white">${result.filename}</td>
                <td class="px-6 py-4">
                    <div class="flex items-center">
                        <span class="mr-2 font-bold text-blue-400">${score}%</span>
                        <div class="w-24 h-2 bg-gray-700 rounded-full overflow-hidden">
                            <div class="h-full bg-blue-500 rounded-full" style="width: ${score}%"></div>
                        </div>
                    </div>
                </td>
                <td class="px-6 py-4 text-right">${statusBadge}</td>
            `;

            // Reason Row (Hidden by default)
            const reasonRow = document.createElement('tr');
            reasonRow.className = 'bg-gray-800/50 hidden border-b border-gray-700';

            // Generate skills HTML
            let skillsHtml = '';
            if (result.skills && result.skills.length > 0) {
                skillsHtml = '<div class="mt-2 flex flex-wrap gap-2">';
                result.skills.slice(0, 10).forEach(skill => {
                    skillsHtml += `<span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-900 text-blue-200">${skill}</span>`;
                });
                skillsHtml += '</div>';
            }

            reasonRow.innerHTML = `
                <td colspan="4" class="px-6 py-4 text-sm text-gray-300">
                    <p class="mb-2"><strong class="text-blue-400">Analysis:</strong> ${result.reason}</p>
                    ${result.highlight ? `
                    <div class="mt-5 relative overflow-hidden rounded-xl border border-blue-500/30 bg-gradient-to-br from-gray-900 to-blue-900/10 p-5 shadow-lg">
                        <div class="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
                        <div class="flex items-start gap-3">
                            <div class="mt-1 flex-shrink-0">
                                <span class="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-500/20 text-blue-400">
                                    <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                                    </svg>
                                </span>
                            </div>
                            <div>
                                <h4 class="text-sm font-semibold text-blue-300 uppercase tracking-wide">AI Spotlight</h4>
                                <p class="mt-2 text-gray-200 leading-relaxed italic">"${result.highlight}"</p>
                            </div>
                        </div>
                    </div>` : ''}
                    ${skillsHtml ? '<p class="text-xs text-gray-500 uppercase tracking-widest mt-4 mb-2">Technical Skills Detected</p>' + skillsHtml : ''}
                </td>
            `;

            // Click event to toggle
            row.style.cursor = 'pointer';
            row.addEventListener('click', () => {
                reasonRow.classList.toggle('hidden');
            });

            // Stagger animation
            row.style.animation = `fadeInUp 0.5s ease-out forwards ${index * 0.1}s`;
            row.style.opacity = '0'; // Start hidden for animation

            resultsBody.appendChild(row);
            resultsBody.appendChild(reasonRow);
        });
    }
});
