//! Stateless CEF 158 helpers, exercised against the linked engine, without a browser.
use cef::sys::cef_dom_key_t as Key;

#[test]
fn official_translation_preserves_logical_keys_and_keypad_location() {
    let unicode = Key::CEF_DOM_KEY_UNICODE_FLAG as u32;
    for (physical, logical, expected) in [
        (0x70037, unicode | '.' as u32, 0xbe),
        (0x70014, unicode | 'a' as u32, 0x41), // AZERTY KeyQ -> a
        (0x7001c, unicode | 'z' as u32, 0x5a), // QWERTZ KeyY -> z
        (0x70004, unicode | 'é' as u32, 0x41), // non-US physical fallback
        (0x70059, unicode | '1' as u32, 0x61), // keypad, not main-row 1
        (0x700e0, Key::CEF_DOM_KEY_ALT as u32, 0x12), // remapped modifier
        (0, Key::CEF_DOM_KEY_DEL as u32, 0x2e),
    ] {
        assert_eq!(
            cef::windows_key_code_from_dom_code_and_key(physical, logical),
            expected
        );
    }
}

#[cfg(target_os = "linux")]
#[test]
fn xkb_helper_separates_named_dead_and_printable_keys() {
    assert_eq!(
        cef::non_printable_dom_key_from_xkeysym(0xffff),
        Key::CEF_DOM_KEY_DEL as u32
    );
    assert_eq!(
        cef::non_printable_dom_key_from_xkeysym(0xfe51),
        Key::CEF_DOM_KEY_DEAD_FLAG as u32 | 0x301
    );
    assert_eq!(cef::non_printable_dom_key_from_xkeysym('.' as u32), 0);
    assert_eq!(cef::non_printable_dom_key_from_xkeysym(0x0101f600), 0);
}
