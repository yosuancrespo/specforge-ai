Feature: Order validation and lifecycle
  As a product team
  We want order behavior to remain aligned with the documented contract
  So that billing and fulfillment defects are caught before release

  Scenario: Reject an order without items
    Given a new order payload with no line items
    When the client submits the order
    Then the API should reject the request
    And the response should explain that at least one item is required

  Scenario: Reject a zero-value order
    Given a new order payload with amount 0
    When the client submits the order
    Then the API should reject the request
    And the response should explain that amount must be positive

  Scenario: Compute the final total correctly
    Given an order with amount 100 and discount 15
    When the client requests the order summary
    Then the final total should be 85

  Scenario: Enforce status transitions
    Given an order in draft state
    When a client tries to move it directly to fulfilled
    Then the API should reject the transition

