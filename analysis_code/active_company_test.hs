import Test.HUnit (Assertion, (@=?), runTestTT, Test(..), Counts(..))
import Test.HUnit.Tools (assertRaises)
import System.Exit (ExitCode(..), exitWith)
import Control.Exception (ErrorCall(ErrorCall))
import ActiveCompany (isActive, activeCompanies)

exitProperly :: IO Counts -> IO ()
exitProperly m = do
  counts <- m
  exitWith $ if failures counts /= 0 || errors counts /= 0 then ExitFailure 1 else ExitSuccess

testCase :: String -> Assertion -> Test
testCase label assertion = TestLabel label (TestCase assertion)

test_bvIsActive :: Assertion
test_bvIsActive =
  True @=? isActive "BV_MV" "ABC;Minerals;1;0"

test_betaInactive :: Assertion
test_betaInactive =
  False @=? isActive "Beta" "ABC;Minerals;1;0"

test_betaInactiveDiv :: Assertion
test_betaInactiveDiv =
  False @=? isActive "Beta" "ABC;Minerals;1;#DIV/0!"

test_betaInactiveRef :: Assertion
test_betaInactiveRef =
  False @=? isActive "Beta" "ABC;Minerals;1;#REF!"

test_invalidIndicator :: Assertion
test_invalidIndicator =
  False @=? isActive "Invalid" "ABC;Minerals;1;0"

test_activeCompanies1:: Assertion
test_activeCompanies1 =
  1 @=? activeCompanies "BV_MV" "Blah\nABC;Minerals;1;0\nBCD;Minerals;0;0"

test_activeCompanies0:: Assertion
test_activeCompanies0 =
  0 @=? activeCompanies "Beta" "Blah\nABC;Minerals;1;0\nBCD;Minerals;0;0"

activeCompanyTests :: [Test]
activeCompanyTests =
  [ testCase "BV is active" test_bvIsActive
   ,testCase "Beta is inactive" test_betaInactive
   ,testCase "Beta is inactive for Div" test_betaInactiveDiv
   ,testCase "Beta is inactive for Ref" test_betaInactiveRef
   ,TestCase (assertRaises "Invalid indicator"
                (ErrorCall "No indicator found") (test_invalidIndicator))
   ,testCase "1 active company for BV_MV" test_activeCompanies1
   ,testCase "0 active companies" test_activeCompanies0
  ]

main :: IO ()
main = exitProperly (runTestTT (TestList activeCompanyTests))
