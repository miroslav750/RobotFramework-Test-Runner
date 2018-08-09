*** Settings ***

Suite Teardown    Close All Browsers
Library           SeleniumLibrary
Library           BuiltIn

*** Test Cases ***
test
    Create WebDriver    Chrome    www.google.sk
    log to console    VSETKO OK
