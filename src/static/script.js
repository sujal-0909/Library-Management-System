// Global variables
let currentUser = null;
let authToken = null;
let currentPage = 1;
let currentSection = 'dashboard';

// API Base URL
const API_BASE = '/api';

// DOM Elements
const elements = {
    navbar: document.getElementById('navbar'),
    mainContent: document.getElementById('main-content'),
    loginModal: document.getElementById('login-modal'),
    registerModal: document.getElementById('register-modal'),
    addBookModal: document.getElementById('add-book-modal'),
    loadingSpinner: document.getElementById('loading-spinner'),
    toastContainer: document.getElementById('toast-container')
};

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    checkAuthStatus();
});

// Initialize application
function initializeApp() {
    // Check if user is logged in
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('currentUser');
    
    if (token && user) {
        authToken = token;
        currentUser = JSON.parse(user);
        showMainContent();
        loadDashboard();
    } else {
        showLoginModal();
    }
}

// Setup event listeners
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', handleNavigation);
    });
    
    // Mobile menu toggle
    document.getElementById('nav-toggle').addEventListener('click', toggleMobileMenu);
    
    // Modal controls
    document.getElementById('close-login').addEventListener('click', () => hideModal('login-modal'));
    document.getElementById('close-register').addEventListener('click', () => hideModal('register-modal'));
    document.getElementById('close-add-book').addEventListener('click', () => hideModal('add-book-modal'));
    
    // Auth switching
    document.getElementById('show-register').addEventListener('click', () => {
        hideModal('login-modal');
        showModal('register-modal');
    });
    
    document.getElementById('show-login').addEventListener('click', () => {
        hideModal('register-modal');
        showModal('login-modal');
    });
    
    // Forms
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    document.getElementById('add-book-form').addEventListener('submit', handleAddBook);
    
    // Logout
    document.getElementById('logout-btn').addEventListener('click', handleLogout);
    
    // Add book button
    document.getElementById('add-book-btn').addEventListener('click', () => {
        if (currentUser && currentUser.username === 'admin') {
            showModal('add-book-modal');
        } else {
            showToast('Only administrators can add books', 'error');
        }
    });
    
    // Filters and search
    document.getElementById('book-search').addEventListener('input', debounce(loadBooks, 500));
    document.getElementById('category-filter').addEventListener('change', loadBooks);
    document.getElementById('available-only').addEventListener('change', loadBooks);
    
    document.getElementById('active-borrowings-only').addEventListener('change', loadBorrowings);
    document.getElementById('overdue-borrowings-only').addEventListener('change', loadBorrowings);
    
    document.getElementById('unpaid-fines-only').addEventListener('change', loadFines);
    
    // Close modals when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    });
}

// Check authentication status
function checkAuthStatus() {
    const token = localStorage.getItem('authToken');
    if (token) {
        authToken = token;
        // Verify token is still valid
        fetch(`${API_BASE}/auth/profile`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Token invalid');
            }
            return response.json();
        })
        .then(data => {
            currentUser = data.member;
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            showMainContent();
            loadDashboard();
        })
        .catch(() => {
            handleLogout();
        });
    }
}

// Navigation handling
function handleNavigation(event) {
    event.preventDefault();
    const section = event.target.getAttribute('data-section');
    if (section) {
        showSection(section);
    }
}

function showSection(sectionName) {
    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');
    
    // Update content
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(`${sectionName}-section`).classList.add('active');
    
    currentSection = sectionName;
    
    // Load section data
    switch(sectionName) {
        case 'dashboard':
            loadDashboard();
            break;
        case 'books':
            loadBooks();
            loadCategories();
            break;
        case 'borrowings':
            loadBorrowings();
            break;
        case 'fines':
            loadFines();
            break;
        case 'profile':
            loadProfile();
            break;
    }
}

// Authentication functions
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('login-username').value;
    const password = document.getElementById('login-password').value;
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            authToken = data.access_token;
            currentUser = data.member;
            
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            
            hideModal('login-modal');
            showMainContent();
            loadDashboard();
            showToast('Login successful!', 'success');
        } else {
            showToast(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const formData = {
        first_name: document.getElementById('register-first-name').value,
        last_name: document.getElementById('register-last-name').value,
        username: document.getElementById('register-username').value,
        email: document.getElementById('register-email').value,
        phone: document.getElementById('register-phone').value,
        address: document.getElementById('register-address').value,
        password: document.getElementById('register-password').value
    };
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            hideModal('register-modal');
            showModal('login-modal');
            showToast('Registration successful! Please login.', 'success');
            document.getElementById('register-form').reset();
        } else {
            showToast(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function handleLogout() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    
    hideMainContent();
    showLoginModal();
    showToast('Logged out successfully', 'success');
}

// Dashboard functions
async function loadDashboard() {
    try {
        showLoading();
        
        // Load statistics
        const [booksResponse, borrowingsResponse, overdueResponse, finesResponse] = await Promise.all([
            fetch(`${API_BASE}/books?per_page=1`, { headers: { 'Authorization': `Bearer ${authToken}` } }),
            fetch(`${API_BASE}/borrowings?active_only=true&per_page=1`, { headers: { 'Authorization': `Bearer ${authToken}` } }),
            fetch(`${API_BASE}/borrowings/overdue`, { headers: { 'Authorization': `Bearer ${authToken}` } }),
            fetch(`${API_BASE}/fines?unpaid_only=true`, { headers: { 'Authorization': `Bearer ${authToken}` } })
        ]);
        
        const booksData = await booksResponse.json();
        const borrowingsData = await borrowingsResponse.json();
        const overdueData = await overdueResponse.json();
        const finesData = await finesResponse.json();
        
        // Update statistics
        document.getElementById('total-books').textContent = booksData.total || 0;
        document.getElementById('borrowed-books').textContent = borrowingsData.total || 0;
        document.getElementById('overdue-books').textContent = overdueData.count || 0;
        
        const totalFines = finesData.fines ? finesData.fines.reduce((sum, fine) => sum + fine.fine_amount, 0) : 0;
        document.getElementById('unpaid-fines').textContent = `$${totalFines.toFixed(2)}`;
        
        // Load recent borrowings
        const recentBorrowingsResponse = await fetch(`${API_BASE}/borrowings?per_page=5`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const recentBorrowingsData = await recentBorrowingsResponse.json();
        
        displayRecentBorrowings(recentBorrowingsData.borrowings || []);
        
        // Load due soon
        const dueSoonResponse = await fetch(`${API_BASE}/borrowings/due-soon`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const dueSoonData = await dueSoonResponse.json();
        
        displayDueSoon(dueSoonData.due_soon_borrowings || []);
        
    } catch (error) {
        showToast('Error loading dashboard', 'error');
    } finally {
        hideLoading();
    }
}

function displayRecentBorrowings(borrowings) {
    const tbody = document.querySelector('#recent-borrowings-table tbody');
    tbody.innerHTML = '';
    
    borrowings.forEach(borrowing => {
        const row = document.createElement('tr');
        const status = borrowing.is_returned ? 'returned' : (new Date(borrowing.due_date) < new Date() ? 'overdue' : 'active');
        
        row.innerHTML = `
            <td>${borrowing.book_title || 'N/A'}</td>
            <td>${formatDate(borrowing.borrow_date)}</td>
            <td>${formatDate(borrowing.due_date)}</td>
            <td><span class="status-badge status-${status}">${status}</span></td>
        `;
        tbody.appendChild(row);
    });
}

function displayDueSoon(borrowings) {
    const tbody = document.querySelector('#due-soon-table tbody');
    tbody.innerHTML = '';
    
    borrowings.forEach(borrowing => {
        const row = document.createElement('tr');
        const dueDate = new Date(borrowing.due_date);
        const today = new Date();
        const daysLeft = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));
        
        row.innerHTML = `
            <td>${borrowing.book_title || 'N/A'}</td>
            <td>${formatDate(borrowing.due_date)}</td>
            <td>${daysLeft} days</td>
            <td>
                <button class="btn btn-sm btn-warning" onclick="renewBook(${borrowing.borrowing_id})">
                    <i class="fas fa-redo"></i> Renew
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Books functions
async function loadBooks() {
    try {
        showLoading();
        
        const search = document.getElementById('book-search').value;
        const category = document.getElementById('category-filter').value;
        const availableOnly = document.getElementById('available-only').checked;
        
        const params = new URLSearchParams({
            page: currentPage,
            per_page: 10,
            ...(search && { search }),
            ...(category && { category }),
            ...(availableOnly && { available_only: 'true' })
        });
        
        const response = await fetch(`${API_BASE}/books?${params}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayBooks(data.books || []);
            updatePagination('books-pagination', data.current_page, data.pages);
        } else {
            showToast(data.error || 'Error loading books', 'error');
        }
    } catch (error) {
        showToast('Network error loading books', 'error');
    } finally {
        hideLoading();
    }
}

function displayBooks(books) {
    const tbody = document.querySelector('#books-table tbody');
    tbody.innerHTML = '';
    
    books.forEach(book => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${book.title}</td>
            <td>${book.author}</td>
            <td>${book.category || 'N/A'}</td>
            <td>${book.available_copies}</td>
            <td>${book.total_copies}</td>
            <td>
                ${book.available_copies > 0 ? 
                    `<button class="btn btn-sm btn-success" onclick="borrowBook(${book.book_id})">
                        <i class="fas fa-book"></i> Borrow
                    </button>` : 
                    '<span class="status-badge status-overdue">Not Available</span>'
                }
                ${currentUser && currentUser.username === 'admin' ? 
                    `<button class="btn btn-sm btn-secondary" onclick="editBook(${book.book_id})">
                        <i class="fas fa-edit"></i> Edit
                    </button>` : ''
                }
            </td>
        `;
        tbody.appendChild(row);
    });
}

async function loadCategories() {
    try {
        const response = await fetch(`${API_BASE}/books/categories`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            const select = document.getElementById('category-filter');
            select.innerHTML = '<option value="">All Categories</option>';
            
            data.categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category;
                option.textContent = category;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

async function handleAddBook(event) {
    event.preventDefault();
    
    const formData = {
        title: document.getElementById('book-title').value,
        author: document.getElementById('book-author').value,
        isbn: document.getElementById('book-isbn').value,
        category: document.getElementById('book-category').value,
        publisher: document.getElementById('book-publisher').value,
        publication_year: parseInt(document.getElementById('book-year').value) || null,
        total_copies: parseInt(document.getElementById('book-copies').value) || 1,
        shelf_location: document.getElementById('book-location').value
    };
    
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/books`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            hideModal('add-book-modal');
            document.getElementById('add-book-form').reset();
            loadBooks();
            loadCategories();
            showToast('Book added successfully!', 'success');
        } else {
            showToast(data.error || 'Error adding book', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function borrowBook(bookId) {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/borrowings/borrow`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({ book_id: bookId })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            loadBooks();
            loadDashboard();
            showToast('Book borrowed successfully!', 'success');
        } else {
            showToast(data.error || 'Error borrowing book', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Borrowings functions
async function loadBorrowings() {
    try {
        showLoading();
        
        const activeOnly = document.getElementById('active-borrowings-only').checked;
        const overdueOnly = document.getElementById('overdue-borrowings-only').checked;
        
        const params = new URLSearchParams({
            page: currentPage,
            per_page: 10,
            ...(activeOnly && { active_only: 'true' }),
            ...(overdueOnly && { overdue_only: 'true' })
        });
        
        const response = await fetch(`${API_BASE}/borrowings?${params}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayBorrowings(data.borrowings || []);
            updatePagination('borrowings-pagination', data.current_page, data.pages);
        } else {
            showToast(data.error || 'Error loading borrowings', 'error');
        }
    } catch (error) {
        showToast('Network error loading borrowings', 'error');
    } finally {
        hideLoading();
    }
}

function displayBorrowings(borrowings) {
    const tbody = document.querySelector('#borrowings-table tbody');
    tbody.innerHTML = '';
    
    borrowings.forEach(borrowing => {
        const row = document.createElement('tr');
        const status = borrowing.is_returned ? 'returned' : (new Date(borrowing.due_date) < new Date() ? 'overdue' : 'active');
        
        row.innerHTML = `
            <td>${borrowing.book_title || 'N/A'}</td>
            <td>${borrowing.member_name || 'N/A'}</td>
            <td>${formatDate(borrowing.borrow_date)}</td>
            <td>${formatDate(borrowing.due_date)}</td>
            <td><span class="status-badge status-${status}">${status}</span></td>
            <td>
                ${!borrowing.is_returned ? 
                    `<button class="btn btn-sm btn-success" onclick="returnBook(${borrowing.borrowing_id})">
                        <i class="fas fa-undo"></i> Return
                    </button>
                    <button class="btn btn-sm btn-warning" onclick="renewBook(${borrowing.borrowing_id})">
                        <i class="fas fa-redo"></i> Renew
                    </button>` : 
                    '<span class="status-badge status-returned">Returned</span>'
                }
            </td>
        `;
        tbody.appendChild(row);
    });
}

async function returnBook(borrowingId) {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/borrowings/${borrowingId}/return`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            loadBorrowings();
            loadDashboard();
            
            if (data.fine_applied) {
                showToast(`Book returned. Fine applied: $${data.fine_applied.amount}`, 'warning');
            } else {
                showToast('Book returned successfully!', 'success');
            }
        } else {
            showToast(data.error || 'Error returning book', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function renewBook(borrowingId) {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/borrowings/${borrowingId}/renew`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            loadBorrowings();
            loadDashboard();
            showToast('Book renewed successfully!', 'success');
        } else {
            showToast(data.error || 'Error renewing book', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Fines functions
async function loadFines() {
    try {
        showLoading();
        
        const unpaidOnly = document.getElementById('unpaid-fines-only').checked;
        
        const params = new URLSearchParams({
            page: currentPage,
            per_page: 10,
            ...(unpaidOnly && { unpaid_only: 'true' })
        });
        
        const response = await fetch(`${API_BASE}/fines?${params}`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayFines(data.fines || []);
            updatePagination('fines-pagination', data.current_page, data.pages);
        } else {
            showToast(data.error || 'Error loading fines', 'error');
        }
    } catch (error) {
        showToast('Network error loading fines', 'error');
    } finally {
        hideLoading();
    }
}

function displayFines(fines) {
    const tbody = document.querySelector('#fines-table tbody');
    tbody.innerHTML = '';
    
    fines.forEach(fine => {
        const row = document.createElement('tr');
        const status = fine.is_paid ? 'paid' : 'unpaid';
        
        row.innerHTML = `
            <td>${fine.member_name || 'N/A'}</td>
            <td>${fine.book_title || 'N/A'}</td>
            <td>$${fine.fine_amount.toFixed(2)}</td>
            <td>${fine.fine_reason}</td>
            <td>${formatDate(fine.fine_date)}</td>
            <td><span class="status-badge status-${status}">${status}</span></td>
            <td>
                ${!fine.is_paid ? 
                    `<button class="btn btn-sm btn-success" onclick="payFine(${fine.fine_id})">
                        <i class="fas fa-dollar-sign"></i> Pay
                    </button>` : 
                    '<span class="status-badge status-paid">Paid</span>'
                }
            </td>
        `;
        tbody.appendChild(row);
    });
}

async function payFine(fineId) {
    showLoading();
    
    try {
        const response = await fetch(`${API_BASE}/fines/${fineId}/pay`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            loadFines();
            loadDashboard();
            showToast('Fine paid successfully!', 'success');
        } else {
            showToast(data.error || 'Error paying fine', 'error');
        }
    } catch (error) {
        showToast('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Profile functions
async function loadProfile() {
    try {
        showLoading();
        
        const [profileResponse, borrowingsResponse, finesResponse] = await Promise.all([
            fetch(`${API_BASE}/auth/profile`, { headers: { 'Authorization': `Bearer ${authToken}` } }),
            fetch(`${API_BASE}/borrowings`, { headers: { 'Authorization': `Bearer ${authToken}` } }),
            fetch(`${API_BASE}/fines`, { headers: { 'Authorization': `Bearer ${authToken}` } })
        ]);
        
        const profileData = await profileResponse.json();
        const borrowingsData = await borrowingsResponse.json();
        const finesData = await finesResponse.json();
        
        if (profileResponse.ok) {
            const member = profileData.member;
            document.getElementById('profile-name').textContent = `${member.first_name} ${member.last_name}`;
            document.getElementById('profile-email').textContent = member.email;
            document.getElementById('profile-member-since').textContent = `Member since ${formatDate(member.membership_date)}`;
            
            // Calculate stats
            const activeBorrowings = borrowingsData.borrowings ? borrowingsData.borrowings.filter(b => !b.is_returned).length : 0;
            const totalBorrowed = borrowingsData.total || 0;
            const unpaidFines = finesData.fines ? finesData.fines.filter(f => !f.is_paid).reduce((sum, f) => sum + f.fine_amount, 0) : 0;
            
            document.getElementById('profile-active-borrowings').textContent = activeBorrowings;
            document.getElementById('profile-total-borrowed').textContent = totalBorrowed;
            document.getElementById('profile-unpaid-fines').textContent = `$${unpaidFines.toFixed(2)}`;
        }
    } catch (error) {
        showToast('Error loading profile', 'error');
    } finally {
        hideLoading();
    }
}

// Utility functions
function showModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

function hideModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

function showMainContent() {
    elements.navbar.style.display = 'block';
    elements.mainContent.style.display = 'block';
}

function hideMainContent() {
    elements.navbar.style.display = 'none';
    elements.mainContent.style.display = 'none';
}

function showLoginModal() {
    showModal('login-modal');
}

function showLoading() {
    elements.loadingSpinner.classList.add('active');
}

function hideLoading() {
    elements.loadingSpinner.classList.remove('active');
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    elements.toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function updatePagination(containerId, currentPage, totalPages) {
    const container = document.getElementById(containerId);
    container.innerHTML = '';
    
    if (totalPages <= 1) return;
    
    // Previous button
    const prevBtn = document.createElement('button');
    prevBtn.textContent = 'Previous';
    prevBtn.disabled = currentPage === 1;
    prevBtn.onclick = () => {
        if (currentPage > 1) {
            this.currentPage = currentPage - 1;
            loadCurrentSection();
        }
    };
    container.appendChild(prevBtn);
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        const pageBtn = document.createElement('button');
        pageBtn.textContent = i;
        pageBtn.className = i === currentPage ? 'active' : '';
        pageBtn.onclick = () => {
            this.currentPage = i;
            loadCurrentSection();
        };
        container.appendChild(pageBtn);
    }
    
    // Next button
    const nextBtn = document.createElement('button');
    nextBtn.textContent = 'Next';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.onclick = () => {
        if (currentPage < totalPages) {
            this.currentPage = currentPage + 1;
            loadCurrentSection();
        }
    };
    container.appendChild(nextBtn);
}

function loadCurrentSection() {
    switch(currentSection) {
        case 'books':
            loadBooks();
            break;
        case 'borrowings':
            loadBorrowings();
            break;
        case 'fines':
            loadFines();
            break;
    }
}

function toggleMobileMenu() {
    const navMenu = document.getElementById('nav-menu');
    navMenu.classList.toggle('active');
}

