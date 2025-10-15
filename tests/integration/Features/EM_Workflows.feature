Feature: EM Workflows tests

  Scenario Outline: New Manuscript creation for PCLMTEST
    When User logins to EM for journal PCLMTEST for scenario <Scenario>
    When 100 manuscripts are created
#    And User clicks New Manuscript
#    And User selects Article Type
#    And User attaches files
#    And User enters General Information
#    And User enters Review Preferences
#    And User enters Additional Information
#    And User enters Comments
#    And User enters Manuscript Data
#    Then Proceed button is disabled
#    And Charges correspond to scenario <Scenario>
#    When User accepts Charges
#    Then Proceed button is enabled
#    And Charges are accepted in Waivers window
#    When User completed Manuscript
    Examples:
      | Scenario |
      | APC      |

  Scenario Outline: New Manuscript creation for PONETEST
    When User logins to EM for journal PONETEST for article type '<ArticleType>' and scenario <Scenario>
    And User clicks New Manuscript
    And User selects Article Type
    And User attaches files
    And User enters General Information
    And User enters Review Preferences
    And User enters Additional Information
    And User enters Comments
    And User enters Manuscript Data
    Then Proceed button is disabled
#    And Charges correspond to scenario <Scenario>
    When User accepts Charges
    Then Proceed button is enabled
    And Charges are accepted in Waivers window
    When User completed Manuscript
    Examples:
      | Scenario      | ArticleType                |
      | APC           | Research Article           |
      | APC           | Clinical Trial             |
      | APC           | Registered Report Protocol |
      | APC           | Registered Report          |
      | APC           | Lab Protocol               |
      | APC           | Study Protocol             |
      | Collections   | Research Article           |
      | Institutional | Research Article           |
      | R4LA          | Research Article           |
      | R4LB          | Research Article           |



#      | APC      | Collection Review                | no waivers
#      | APC      | Overview                         | no waivers
#      | APC      | Formal Comment (invitation only) | no waivers

  Scenario Outline: New Manuscript creation
    When User logins to EM for journal PGPHTEST for scenario <Scenario>
    And User clicks New Manuscript
    And User selects Article Type
    And User attaches files
    And User enters General Information
    And User enters Review Preferences
    And User enters Additional Information
    And User enters Comments
    And User enters Manuscript Data
    Then Proceed button is disabled
    And Charges correspond to scenario <Scenario>
    When User accepts Charges
    Then Proceed button is enabled
    And Charges are accepted in Waivers window
    When User completed Manuscript
    Examples:
      | Scenario |
      | APC      |
#      | Collections   |
#      | Institutional |
#      | R4LA          |
#      | R4LB          |

  Scenario Outline: PFA scenario
    When User logins to EM for journal <journal> for scenario PFA
    And User clicks New Manuscript
    And User selects Article Type
    And User attaches files
    And User enters General Information
    And User enters Review Preferences
    And User enters Additional Information
    And User enters Comments
    And User enters Manuscript Data
    Then Proceed button is disabled
    When User applies for PFA with <answers> answers
    Then Alchemer page is opened
    When User uploads a file to Alchemer
    Then Upload is successfull
    Then Proceed button is enabled
    And Charges are accepted in Waivers window
    When User completed Manuscript
    Then SalesForce Case has corrent information
    Examples:
      | journal  | answers |
      | PGPHTEST | Yes     |
      | PGPHTEST | No      |
#      | PONETEST | Yes     |
#      | PONETEST | No      |
