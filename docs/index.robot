*** Test Cases ***
Withdraw From Account
  [tags]  user  withdraw
  ${status} =   Withdraw From Account    $50
  Withdraw Should Have Succeeded     ${status}

*** Keywords ***
Withdraw From Account
  [arguments]   ${amount}
  ${status} =   Withdraw From User Account  ${USER}  ${amount}
  [return]      ${status}

Withdraw Should Have Succeeded
  [arguments]   ${status}
  Should Be Equal   ${status}   SUCCESS
