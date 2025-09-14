base url =http://127.0.0.1:8000/

authentication 

POST /account/register/
BODY:{username,email,first_name,last_name,password,confirm_password}

(only owner can get,put,patch)

GET ,PATCH,PUT /account/2/

(only owner can change his password)
POST account/passwordchange/2/
BODY:{old_password,new_password}



POST /send_otp_for_password_reset/
BODY:{email}

POST /reset_password/

BODY:{email,otp,new_password}


POST /account/login/
BODY;{username,password}

POST /account/logout/
