# 패스워드 처리하는 함수를 적는다 
           # 해쉬는 문자나 숫자를  다른 문자나 숫자로 바꾸고 유니크하게 만들어준다 
from passlib.hash import pbkdf2_sha256

from config.config import salt

# (패스워드가 들어오면 해당 패스워드를 암호화 해줌)
# 회원가입시 사용할 함수로서, 유저가 입력한 비밀번호를 암호화 해주는 함수
def hash_password(password) :
                                         # salt 이게 패스워드 앞뒤로 들어갈수잇고 이안에 들어있는건 절대 알려주지 않는다 회사마다 다르니 그래서 해킹이 힘들어진다
    return pbkdf2_sha256.hash(password + salt) 

# 로그인시 사용할 함수로서
# 유저가 입력한 패스워드도 받아오고 db에 저장되어 있는 패스워드도 받아와서 같은지 확인해주는 함수
def check_password(password, hashed) :
    return pbkdf2_sha256.verify(password + salt, hashed)