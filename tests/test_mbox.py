import pytest  # noqa
import os
import b4
import b4.mbox
import b4.command


@pytest.mark.parametrize('mboxf, msgid, shazamargs, compareargs, compareout, b4cfg', [
    ('shazam-git1-just-series', '20221025-test1-v1-0-e4f28f57990c@linuxfoundation.org',
     [], ['log', '--format=%ae%n%s%n%b---', 'HEAD~4..'], 'shazam-git1-just-series-defaults', []),
])
def test_shazam(sampledir, gitdir, mboxf, msgid, shazamargs, compareargs, compareout, b4cfg):
    b4.MAIN_CONFIG.update(b4cfg)
    mfile = os.path.join(sampledir, f'{mboxf}.mbox')
    cfile = os.path.join(sampledir, f'{compareout}.verify')
    assert os.path.exists(mfile)
    assert os.path.exists(cfile)
    parser = b4.command.setup_parser()
    shazamargs = ['shazam', '-m', mfile] + shazamargs + [msgid]
    cmdargs = parser.parse_args(shazamargs)
    with pytest.raises(SystemExit) as e:
        b4.mbox.main(cmdargs)
        assert e.type == SystemExit
        assert e.value.code == 0
    out, logstr = b4.git_run_command(None, compareargs)
    assert out == 0
    with open(cfile, 'r') as fh:
        cstr = fh.read()
    assert logstr == cstr
