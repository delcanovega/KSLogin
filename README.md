# KSLogin
KSLogin — which stands for KeyStroke Login — is a web application that will use machine learning techniques to authenticate a person's identity through his keystroke biometrics.
### Features used:
* Average pressing key time.
* Average flight time between keys.
* The number of mistakes.
* The number of keys pressed over the necessary ones. This can be interpreted in different ways:
  - If the number is slightly over 0: the user probably early realized his mistakes and corrected them.
  - If the number is higly over 0: the user had a lot of mistakes, or a few but he realised about them at the end of the   word.
  - If the number is negative: Man, that's weird. But also mi python is very shitty at this point so don't worry.
* Does the user hit the Caps Lock key or prefer the Shift?.
### Recommendations:
For proper operation, it is recommended that each profile is trained at least 50 times.
