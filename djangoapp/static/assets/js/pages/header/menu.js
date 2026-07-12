// Arquivo dedicado à lógica do menu de perfil do usuário, 
// incluindo a abertura e fechamento do dropdown. 

const MenuActions = {
    toggleProfileMenu(e) {
        if (e) e.stopPropagation(); // Evita que o clique feche o menu imediatamente
        const dropdown = document.getElementById('profile-dropdown');
        if (dropdown) {
            dropdown.classList.toggle('active');
        }
    },

    openProfileMenu() {
        const dropdown = document.getElementById('profile-dropdown');
        if (dropdown && !dropdown.classList.contains('active')) {
            dropdown.classList.add('active');
        }
    },

    closeProfileMenu() {
        const dropdown = document.getElementById('profile-dropdown');
        if (dropdown && dropdown.classList.contains('active')) {
            dropdown.classList.remove('active');
        }
    }
}

const init = () => {
    const profileMenuTrigger = document.getElementById('profile-menu-trigger');
    const profileContainer = document.querySelector('.profile-menu-container');
    if (profileMenuTrigger) {
        profileMenuTrigger.addEventListener('click', MenuActions.toggleProfileMenu); // abrir menu ao clicar no ícone
        profileMenuTrigger.addEventListener('mouseenter', MenuActions.openProfileMenu); // abrir ao passar mouse por cima
    }

    if (profileContainer) {
        // Fecha o menu apenas quando o mouse sair de toda a área do container (ícone + menu)
        profileContainer.addEventListener('mouseleave', MenuActions.closeProfileMenu);
    } 

    document.addEventListener('click', MenuActions.closeProfileMenu); // fecha o menu de perfil ao clicar fora dele
}

init();