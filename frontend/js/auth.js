// MILO Authentication Client: Login, registration, and onboarding redirection.

document.addEventListener('DOMContentLoaded', () => {
    initModeSwitcher();
    initPasswordToggles();
    initLoginForm();
    initRegisterForm();
    checkExistingAuth();
});

function getQueryParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
}

function checkExistingAuth() {
    const token = localStorage.getItem('milo_token');
    const user = localStorage.getItem('milo_user');
    if (token && user && !getQueryParam('force')) {
        const redirect = getQueryParam('redirect') || 'dashboard.html';
        window.location.href = redirect;
    }
}

function initModeSwitcher() {
    const tabLogin = document.getElementById('tabBtnLogin');
    const tabRegister = document.getElementById('tabBtnRegister');
    const panelLogin = document.getElementById('panelLogin');
    const panelRegister = document.getElementById('panelRegister');
    const switchToRegister = document.getElementById('switchToRegister');
    const switchToLogin = document.getElementById('switchToLogin');

    function setMode(mode) {
        clearAlert('authAlertContainer');
        if (mode === 'register') {
            if (tabLogin) {
                tabLogin.classList.remove('active');
                tabLogin.setAttribute('aria-selected', 'false');
            }
            if (tabRegister) {
                tabRegister.classList.add('active');
                tabRegister.setAttribute('aria-selected', 'true');
            }
            if (panelLogin) panelLogin.classList.remove('active');
            if (panelRegister) panelRegister.classList.add('active');
            document.title = 'Daftar Akun Baru: MILO English Speaking Practice';
        } else {
            if (tabLogin) {
                tabLogin.classList.add('active');
                tabLogin.setAttribute('aria-selected', 'true');
            }
            if (tabRegister) {
                tabRegister.classList.remove('active');
                tabRegister.setAttribute('aria-selected', 'false');
            }
            if (panelLogin) panelLogin.classList.add('active');
            if (panelRegister) panelRegister.classList.remove('active');
            document.title = 'Masuk ke Akun: MILO English Speaking Practice';
        }
    }

    if (tabLogin) {
        tabLogin.addEventListener('click', () => setMode('login'));
    }
    if (tabRegister) {
        tabRegister.addEventListener('click', () => setMode('register'));
    }
    if (switchToRegister) {
        switchToRegister.addEventListener('click', () => setMode('register'));
    }
    if (switchToLogin) {
        switchToLogin.addEventListener('click', () => setMode('login'));
    }

    const modeParam = getQueryParam('mode');
    const isRegisterPage = window.location.pathname.endsWith('register.html');
    if (modeParam === 'register' || (isRegisterPage && modeParam !== 'login')) {
        setMode('register');
    } else {
        setMode('login');
    }
}

function initPasswordToggles() {
    const toggleButtons = document.querySelectorAll('.btn-toggle-password');
    toggleButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            const input = document.getElementById(targetId);
            if (!input) return;

            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';

            const icon = btn.querySelector('i');
            if (icon) {
                icon.className = isPassword ? 'fa-solid fa-eye-slash' : 'fa-solid fa-eye';
            }
            btn.setAttribute('aria-label', isPassword ? 'Sembunyikan kata sandi' : 'Tampilkan kata sandi');
        });
    });
}

function showAlert(containerId, message, type = 'error') {
    const container = document.getElementById(containerId);
    if (!container) return;

    const iconClass = type === 'error' ? 'fa-triangle-exclamation' : 'fa-circle-check';
    container.innerHTML = `
        <div class="auth-alert ${type}" role="alert">
            <i class="fa-solid ${iconClass} auth-alert-icon"></i>
            <div>${escapeHtml(message)}</div>
        </div>
    `;
    container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function clearAlert(containerId) {
    const container = document.getElementById(containerId);
    if (container) container.innerHTML = '';
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function initLoginForm() {
    const form = document.getElementById('loginForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearAlert('authAlertContainer');

        const identifier = document.getElementById('loginIdentifier')?.value.trim();
        const password = document.getElementById('loginPassword')?.value;
        const submitBtn = document.getElementById('btnLoginSubmit');

        if (!identifier || !password) {
            showAlert('authAlertContainer', 'Silakan masukkan username/email dan kata sandi Anda.');
            return;
        }

        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Masuk...';

        try {
            const response = await fetch('/api/v1/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: identifier, password: password }),
            });

            const data = await response.json();

            if (!response.ok) {
                const message = data.detail || 'Gagal masuk. Periksa kembali username dan kata sandi Anda.';
                showAlert('authAlertContainer', message, 'error');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
                return;
            }

            localStorage.setItem('milo_token', data.access_token);
            localStorage.setItem('milo_user', JSON.stringify(data.user));

            showAlert('authAlertContainer', 'Berhasil masuk. Mengalihkan ke dashboard...', 'success');

            const destination = getQueryParam('redirect') || 'dashboard.html';
            setTimeout(() => {
                window.location.href = destination;
            }, 600);
        } catch (err) {
            showAlert('authAlertContainer', 'Terjadi gangguan koneksi ke server. Pastikan backend MILO sedang berjalan.', 'error');
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        }
    });
}

function initRegisterForm() {
    const form = document.getElementById('registerForm');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearAlert('authAlertContainer');

        const username = document.getElementById('regUsername')?.value.trim();
        const fullName = document.getElementById('regFullName')?.value.trim();
        const email = document.getElementById('regEmail')?.value.trim();
        const password = document.getElementById('regPassword')?.value;
        const confirmPassword = document.getElementById('regConfirmPassword')?.value;

        const submitBtn = document.getElementById('btnRegisterSubmit');

        if (!username) {
            showAlert('authAlertContainer', 'Username wajib diisi.');
            return;
        }

        if (username.length < 3 || username.length > 30) {
            showAlert('authAlertContainer', 'Username harus antara 3 hingga 30 karakter.');
            return;
        }

        if (!/^[a-zA-Z0-9_.-]+$/.test(username)) {
            showAlert('authAlertContainer', 'Username hanya boleh berisi huruf, angka, titik, strip, atau garis bawah.');
            return;
        }

        if (!password || password.length < 6) {
            showAlert('authAlertContainer', 'Kata sandi minimal 6 karakter.');
            return;
        }

        if (password !== confirmPassword) {
            showAlert('authAlertContainer', 'Konfirmasi kata sandi tidak cocok.');
            return;
        }

        const originalBtnText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Mendaftarkan...';

        try {
            const payload = {
                username: username,
                password: password,
                cefr_level: 'B1',
            };
            if (fullName) payload.full_name = fullName;
            if (email) payload.email = email;

            const response = await fetch('/api/v1/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload),
            });

            const data = await response.json();

            if (!response.ok) {
                const message = data.detail || 'Pendaftaran gagal. Silakan coba kembali.';
                showAlert('authAlertContainer', message, 'error');
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
                return;
            }

            const userObj = data.user || {};
            localStorage.setItem('milo_token', data.access_token);
            localStorage.setItem('milo_user', JSON.stringify(userObj));

            showAlert('authAlertContainer', 'Akun berhasil dibuat. Melanjutkan ke penentuan level...', 'success');

            setTimeout(() => {
                window.location.href = 'setup-level.html';
            }, 650);
        } catch (err) {
            showAlert('authAlertContainer', 'Terjadi gangguan koneksi ke server. Pastikan backend MILO sedang berjalan.', 'error');
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        }
    });
}
