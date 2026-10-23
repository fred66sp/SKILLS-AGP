# Fixture de referencia del nivel NO APTO: lleva al menos una violación de cada código que
# comprueba scripts/check-feature.py. El dominio es el desarrollo de software (build de
# documentación, CLI, pipeline de CI y validador), no la compra de un producto.
#   business-intent-given, low-level-vocab, person-mixed, too-many-steps -> "Publish the site"
#   step-order, multiple-action-outcome                                  -> "Edit the pipeline config"
#   multiple-action-outcome, no-subject-verb                             -> "Search build logs"
#   missing-then                                                         -> "Check the report"
#   unparseable-block                                                    -> escenario sin título
#   redundant-examples, outline-missing-placeholder                      -> "Validate findings"
Feature: Documentation build pipeline
  As a maintainer
  I want the build to fail on broken links
  So that we never publish unusable guides

  Background:
    Given the repository is on the main branch
    And the docs compiler is installed

  Scenario: Publish the site
    Given I want the documentation to be published
    When I open the browser at https://ci.example.com
    And I click the "Run pipeline" button
    And I type my password in the login form
    And I type my token
    And I wait two seconds
    And I click the "Artifacts" tab
    And I scroll down the log list
    And I download the build log
    Then the maintainer sees the published site

  Scenario: Edit the pipeline config
    When the developer opens the config file
    Then the config file shows the cache directory
    Given the developer edits the cache directory
    When the developer saves the config file
    Then the config file shows the new cache directory

  Scenario: Search build logs
    Given the developer is on the build page
    When the developer searches for "timeout"
    Then results for "timeout" are shown
    When the developer opens the error tab
    Then error rows

  Scenario: Check the report
    Given the build has finished
    When the maintainer opens the report

  Scenario:
    Given a scenario with no title

  Scenario Outline: Validate findings
    Given the validator analyses a document with "<finding>"
    When the compiler finishes the review
    Then the report marks the finding with "<severity>"
    And the report stores the row limit "<row limit>"

    Examples:
      | finding             | severity | cache dir |
      | broken link         | error    | a         |
      | duplicate title     | warning  | b         |
      | missing heading     | warning  | c         |
      | orphan asset        | warning  | d         |
      | stale include       | warning  | e         |
      | broken anchor       | error    | f         |
      | duplicate anchor    | error    | g         |
      | broken row          | error    | h         | i        |
