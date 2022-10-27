import pytest  # noqa
import os
import b4
import b4.ez
import b4.mbox
import b4.command


@pytest.fixture(scope="function")
def prepdir(gitdir):
    parser = b4.command.setup_parser()
    b4args = ['--no-stdin', '--no-interactive', '--offline-mode', 'prep', '-n', 'pytest']
    cmdargs = parser.parse_args(b4args)
    b4.ez.cmd_prep(cmdargs)
    yield gitdir


@pytest.mark.parametrize('mboxf, trargs, compareargs, compareout, b4cfg', [
    ('trailers-thread-with-followups', [],
     ['log', '--format=%ae%n%s%n%b---', 'HEAD~4..'], 'trailers-thread-with-followups',
     {'shazam-am-flags': '--signoff'}),
    ('trailers-thread-with-cover-followup', [],
     ['log', '--format=%ae%n%s%n%b---', 'HEAD~4..'], 'trailers-thread-with-cover-followup',
     {'shazam-am-flags': '--signoff'}),
])
def test_trailers(sampledir, prepdir, mboxf, trargs, compareargs, compareout, b4cfg):
    b4.MAIN_CONFIG.update(b4cfg)
    config = b4.get_main_config()
    assert config.get('shazam-am-flags') == '--signoff'
    mfile = os.path.join(sampledir, f'{mboxf}.mbox')
    cfile = os.path.join(sampledir, f'{compareout}.verify')
    assert os.path.exists(mfile)
    assert os.path.exists(cfile)
    parser = b4.command.setup_parser()
    b4args = ['--no-stdin', '--no-interactive', '--offline-mode', 'shazam', '--no-add-trailers', '-m', mfile]
    cmdargs = parser.parse_args(b4args)
    with pytest.raises(SystemExit) as e:
        b4.mbox.main(cmdargs)
        assert e.type == SystemExit
        assert e.value.code == 0

    parser = b4.command.setup_parser()
    b4args = ['--no-stdin', '--no-interactive', '--offline-mode', 'trailers', '--update', '-m', mfile] + trargs
    cmdargs = parser.parse_args(b4args)
    b4.ez.cmd_trailers(cmdargs)

    out, logstr = b4.git_run_command(None, compareargs)
    assert out == 0
    with open(cfile, 'r') as fh:
        cstr = fh.read()
    assert logstr == cstr

