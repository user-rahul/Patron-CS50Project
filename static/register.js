document.addEventListener('DOMContentLoaded', () => {

    const loginForm = document.querySelector("form.login");

    const loginBtn = document.querySelector("label.login");

    const signupBtn = document.querySelector("label.signup");

    const signupLink = document.querySelector("form .signup-link a");

    signupBtn.onclick = (()=>{
        loginForm.style.marginLeft = "-50%";
    });

    loginBtn.onclick = (()=>{
        loginForm.style.marginLeft = "0%";
    });

    signupLink.onclick = (()=>{
        signupBtn.click();
        return false;
    });
});